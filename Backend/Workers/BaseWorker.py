import ast
import logging

from typing import List, Tuple, Any, Dict
from flask_socketio import emit

from AiOrchestration.AiModel import AiModel
from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Exceptions import FAILURE_TO_REVIEW_RELEVANT_HISTORY
from Data.Configuration import Configuration
from Data.InternetSearch import InternetSearch
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Data.UserContextManagement import UserContextManagement
from Constants.Instructions import DEFAULT_BEST_OF_SYSTEM_MESSAGE, DETECT_RELEVANT_HISTORY_SYSTEM_MESSAGE
from Utilities.Contexts import get_category_context
from Utilities.Validation import is_valid_prompt
from Workflows.ChatWorkflow import ChatWorkflow


class BaseWorker:
    """
    Base class for creating workers that execute tasks.

    :param name: Name of the worker.

    history: Note that history is written first on the left, latest on the right, but OpenAI uses latest on
    the left, first on the right. Therefore, it must be reversed if submitted to OpenAI API as messages.
    """

    MAX_HISTORY = 5
    WORKFLOWS: Dict[str, Any] = {
        'chat': ChatWorkflow(),
    }

    def __init__(self, name: str):
        self.name = name
        self.history: List[Tuple[str, str]] = []  # question-response pairs
        self.instructions = ""
        self.configuration = ""

    def query(self,
              user_prompt: str,
              file_references: List[str] = None,
              selected_message_ids: List[str] = None,
              tags: List[str] = None) -> Any:
        """
        Handles a user prompt

        :param user_prompt: User input prompt.
        :param file_references: Additional file references paths, format <category_id>/<file_name_with_extension>.
        :param selected_message_ids: UUIDs of previously selected relevant messages to review.
        :param tags: Additional information for prompting, e.g., if and where to write a file.
        """
        if is_valid_prompt(user_prompt):
            return self.select_workflow(user_prompt, file_references, selected_message_ids, tags)
        else:
            logging.error("Invalid input. Please ask a clear and valid question.")

    def select_workflow(self,
                        initial_message: str,
                        file_references: List[str] = None,
                        selected_message_ids: List[str] = None,
                        tags: List[str] = None) -> Any:
        """
        Determines and executes the appropriate workflow based on user input and tags.

        :param initial_message: The user's initial message or prompt.
        :param file_references: List of file paths referenced in the workflow.
        :param selected_message_ids: UUIDs of previously selected messages for context.
        :param tags: Additional tags to influence workflow selection.
        :return: The last response message from the executed workflow.
        """
        tags = tags or {}
        workflow_key = self._determine_workflow_key(tags)

        if workflow_key:
            return self.execute_workflow(
                workflow_key,
                self.process_prompt,
                initial_message,
                file_references,
                selected_message_ids,
                tags
            )

        # Handle case where no valid workflow key is found
        return self.execute_workflow(
            "chat",
            self.process_prompt,
            initial_message,
            file_references,
            selected_message_ids,
            tags
        )

    @staticmethod
    def _determine_workflow_key(tags: Dict[str, str]) -> str | None:
        """
        Determines the workflow key based on tags.

        :param tags: A dictionary of tags provided by the user.
        :return: The key of the selected workflow or None if not found.
        """
        return tags.get("workflow", None)

    def execute_workflow(self, name: str, *args, **kwargs) -> Any:
        """
        Executes the specified workflow.

        :param name: Name of the workflow.
        :param args: Positional arguments for the workflow.
        :param kwargs: Keyword arguments for the workflow.
        :return: The result of the workflow execution.
        :raises ValueError: If the workflow does not exist.
        """
        if name not in self.WORKFLOWS.keys():
            logging.error(f"Workflow '{name}' not found.")
            raise ValueError(f"Workflow '{name}' not found.")

        logging.info(f"Executing workflow '{name}'.")
        emit("update_workflow", {"status": "in-progress"})

        result = self.WORKFLOWS[name].execute(*args, **kwargs)
        return result

    def process_prompt(
        self,
        prompt: str,
        file_references: List[str] = None,
        selected_message_ids: List[str] = None,
        best_of: int = 1,
        loops: int = 1,
        streaming: bool = False,
        model: AiModel = None
    ) -> str:
        """
        Process and store the user's question.

        :param prompt: The user's question.
        :param file_references: List of file paths referenced for context.
        :param selected_message_ids: UUIDs of previously selected relevant messages result.
        :param best_of: Number of simultaneous parallel re-runs
        :param loops: Number of sequential re-runs
        :param streaming: Whether to stream the response.
        :param model: The model to use for generating responses.
        :return: Generated response.
        """
        file_content = []
        for file_reference in file_references:
            content = StorageMethodology.select().read_file(file_reference)
            logging.info(f"Extracting file content [{file_reference}]: {content}")
            file_content.append(content)

        messages = []
        if selected_message_ids:
            for message_id in selected_message_ids:
                message = nodeDB().get_message_by_id(message_id)
                content = message["prompt"] + " : \n\n" + message["response"]
                messages.append(content)

        config = Configuration.load_config()
        if config['response_improvement'].get('internet_search_enabled', False) == 'on':
            internet_search_results = InternetSearch().search_internet_based_on_prompt(prompt)
            for search_result in internet_search_results:
                messages.append(str(search_result))

        logging.info(f"Message content: {messages}")

        input_messages = file_content + [prompt]
        response = self.think(
            input_messages,
            messages,
            best_of=best_of,
            loops=loops,
            streaming=streaming,
            model=model
        )
        self.history.append((prompt, response))

        return response

    def think(
        self,
        user_messages: List[str],
        history_messages: List[str] = None,
        best_of: int = 1,
        loops: int = 1,
        streaming: bool = False,
        model: AiModel = None
    ) -> str:
        """
        Process the input question and create a response.

        ToDo: How the application accesses and gives history to the llm will need to be optimised

        :param user_messages: List of user messages.
        :param history_messages: The ai will treat these messages as prior context
        :param best_of: How many times this 'thought' is to be rerun to select for a best response
        :param loops: How many 'thoughts' to think before returning a (hopefully) well thought out response
        :param streaming: Whether to stream the response.
        :param model: The AI model used for generating the response.
        :return: Generated response or an error message.
        """
        logging.info("Processing user messages: %s", user_messages)

        config = Configuration.load_config()

        system_messages = [self.instructions, self.configuration]

        if config['category'].get('category_system_message', True):
            category_system_message = nodeDB().get_category_system_message(get_category_context())
            if category_system_message:
                system_messages.append(category_system_message)

        if config['response_improvement']['user_context_enabled']:
            user_encyclopedia_manager = UserContextManagement()
            user_context = user_encyclopedia_manager.search_encyclopedia(user_messages)
            if user_context:
                system_messages.append(user_context)

        if config['optimisation']['message_history']:
            recent_history = self.detect_relevant_history(user_messages)
        else:
            recent_history = [f"{entry[0]}: {entry[1]}" for entry in self.history[-self.MAX_HISTORY:]]
        recent_history.extend(history_messages)

        best_of_system_message = config['system_messages'].get(
            "best_of_message",
            DEFAULT_BEST_OF_SYSTEM_MESSAGE
        )
        judgement_criteria = (
            best_of_system_message +
            f"\n<user_message>{user_messages}</user_message>"
        )

        try:
            output = AiOrchestrator().execute(
                system_messages,
                user_messages,
                rerun_count=best_of,
                loop_count=loops,
                judgement_criteria=[judgement_criteria],  # should be refactored to an obviously plural argument name
                model=model,
                assistant_messages=recent_history,
                streaming=streaming
            )
            return output
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

    def detect_relevant_history(self, user_messages: List[str]) -> List[str]:
        """
        ⚠ WIP

        Automatically determine which prompt-response pairs are relevant for the current context.

        ToDo: latter this project would probably be better suited extracting 'concepts' from prompts, these concepts
         would be keywords that can then relate *back* to the knowledge base, user knowledge, history, configuration,
         worker, workflow, etc. With contexts having different strengths based on the input prompt and response

        :param user_messages: List of messages inputted by the user.
        :return: Relevant history entries.
        """
        numbered_prompts = "Prompt History: " + "\n".join(
            [f"{idx}: {entry[0]}" for idx, entry in enumerate(self.history)]
        )

        executor = AiOrchestrator()
        relevant_history_list = executor.execute(
            [DETECT_RELEVANT_HISTORY_SYSTEM_MESSAGE,
             numbered_prompts],
            user_messages
        )
        logging.info(f"Relevant messages detected in history: {relevant_history_list}")

        relevant_history = []
        try:
            relevant_history_list = ast.literal_eval(relevant_history_list)
            if relevant_history_list:
                for id in relevant_history_list:
                    relevant_history.append(str(self.history[int(id)]))
        except Exception:
            logging.exception(FAILURE_TO_REVIEW_RELEVANT_HISTORY)

        return relevant_history
