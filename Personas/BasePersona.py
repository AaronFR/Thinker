import ast
import logging
from typing import List, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration

from Data.EncyclopediaManagement import EncyclopediaManagement
from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Data.UserContextManagement import UserContextManagement
from Personas.PersonaSpecification.PersonaConstants import SELECT_WORKFLOW_INSTRUCTIONS
from Utilities.ErrorHandler import ErrorHandler
from Utilities.UserContext import get_user_context
from Utilities.Utility import Utility


class BasePersona:
    """
    Base class for creating personas that execute tasks.

    history: Note that history is written first on the left, latest on the right, but openAi uses latest on
    the left, first on the right. So it must be reversed if put into openAi API as messages
    """
    MAX_HISTORY = 5

    def __init__(self, name):
        self.name = name
        self.history: List[Tuple[str, str]] = []  # question-response pairs
        self.workflows = {}
        self.instructions = ""
        self.configuration = ""

        ErrorHandler.setup_logging()

    def query(self,
              user_prompt: str,
              file_references: List[str] = None,
              selected_message_ids: List[str] = None,
              tags: List[str] = None):
        """
        Handles a user prompt

        ToDo adding to the user_encyclopedia needs to be influenced by context category

        :param user_prompt: user input prompt
        :param file_references: additional file references paths, format <category_id>/<file_name_with_extension>
        :param selected_message_ids: the uuids of previous selected relevant messages to review
        :param tags: additional information for prompting, e.g. if and where to write a file
        """
        if Utility.is_valid_prompt(user_prompt):
            return self.run_workflow(user_prompt, file_references, selected_message_ids, tags)
        else:
            print("Invalid input. Please ask a clear and valid question.")

    def chat_workflow(self,
                      initial_message: str,
                      file_references: List[str] = None,
                      selected_message_ids: List[str] = None,
                      tags: List[str] = None):
        raise NotImplementedError("Default workflow is to be implemented in specific persona")

    def query_user_for_input(self):
        """
        Continuously prompts the user for questions until they choose to exit.
        For debugging the backend from the terminal.
        """
        config = Configuration.load_config()
        while True:
            user_input = input("Please enter your task (or type 'exit' to quit): ")
            if Utility.is_exit_command(user_input):
                print("Exiting the question loop.")
                break
            elif user_input.lower() == 'history':
                self.display_history()
            elif Utility.is_valid_prompt(user_input):
                self.select_workflow(user_input)
            else:
                print("Invalid input. Please ask a clear and valid question.")

    def display_history(self):
        """Display the conversation history to the user.
        If there is no history available, a message is shown.
        """
        if not self.history:
            print("No interaction history available.")
            return
        print("Interaction History:")
        for i, (question, response) in enumerate(self.history):
            print(f"{i + 1}: Q: {question}\n    A: {response}")

    def select_workflow(self, initial_message: str, file_references: List[str] = None):
        """Determine and run the appropriate workflow based on the user's query"""
        executor = AiOrchestrator()
        output = executor.execute_function(
            [
                f"Given what my next task is, which of the following workflows is the most appropriate? "
                f"Just select which workflow is most appropriate.\nWorkflows: {self.workflows}"
            ],
            [initial_message],
            SELECT_WORKFLOW_INSTRUCTIONS
        )
        selected_workflow = output['selection']

        logging.info(f"Selected workflow: {selected_workflow}")
        return self.run_workflow(selected_workflow, initial_message, file_references)

    def run_workflow(self,
                     selected_workflow: str,
                     initial_message: str,
                     file_references: List[str] = None,
                     selected_message_ids: List[str] = None):
        raise NotImplementedError("This method should be overridden by subclasses")

    def process_question(
        self,
        question: str,
        file_references: List[str] = None,
        selected_message_ids: List[str] = None,
        streaming: bool = False
     ):
        """Process and store the user's question.

        :return response: stream"""
        file_content = []
        for file_reference in file_references:
            content = FileManagement.read_file_full_address(file_reference)
            logging.info(f"Extracting file content [{file_reference}]: {content}")
            file_content.append(content)

        ndm = NodeDatabaseManagement()

        messages = []
        if selected_message_ids:
            for message_id in selected_message_ids:
                message = ndm.get_message_by_id(message_id)
                content = message["prompt"] + " : \n\n" + message["response"]
                messages.append(content)
        logging.info(f"Message content: {messages}")

        input_messages = [question] + file_content
        response = self.think(input_messages, messages, streaming)
        self.history.append((question, response))
        return response

    def think(
        self,
        user_messages: List[str],
        previous_messages: List[str] = None,
        streaming: bool = False
    ) -> str:
        """Process the input question and think through a response.
        ToDo: this will be called multiple times redundantly in a workflow, user_messages are small however and the
         context can change from step to step so its not a priority
        ToDo: split additional_context lists up before sending on
        ToDo: How the application accesses and gives history to the llm will need to be optimised

        :param user_messages: List of existing user message
        :param previous_messages: prior messages selected as context for this prompt
        :return The generated response stream or an error message
        """
        logging.info("Processing user messages: %s", user_messages)

        staged_files = FileManagement.list_staged_files()
        executor = AiOrchestrator(staged_files)
        config = Configuration.load_config()

        system_messages = [self.instructions, self.configuration]

        if config['beta_features']['encyclopedia_enabled']:
            encyclopedia_manager = EncyclopediaManagement()
            additional_context = encyclopedia_manager.search_encyclopedia(user_messages)
            system_messages.append(additional_context)

        if config['beta_features']['user_context_enabled']:
            user_encyclopedia_manager = UserContextManagement()
            user_context = user_encyclopedia_manager.search_encyclopedia(user_messages)
            system_messages.append(user_context)

        if config['optimization']['message_history']:
            recent_history = self.detect_relevant_history(user_messages)
        else:
            recent_history = [f"{entry[0]}: {entry[1]}" for entry in self.history[-self.MAX_HISTORY:]]

        recent_history.extend(previous_messages)

        try:
            output = executor.execute(
                system_messages,
                user_messages,
                assistant_messages=recent_history,
                streaming=streaming
            )
            return output
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

    def detect_relevant_history(self, user_messages: List[str]) -> List[str]:
        """
        Uses an ai call to actually determine which prompt - response pairs to send on

        ToDo: latter this project would probably be better suited extracting 'concepts' from prompts, these concepts
         would be keywords that can then relate *back* to the knowledge base, user knowledge, history, configuration,
         persona, workflow, etc. With contexts having different strengths based on the input prompt and response

        :param user_messages:
        :return:
        """
        numbered_prompts = "Prompt History: " + "\n".join(
            [f"{idx}: {entry[0]}" for idx, entry in enumerate(self.history)]
        )

        executor = AiOrchestrator()
        relevant_history_list = executor.execute(
            ["Review the messages I've entered and am about to enter, check them against the Prompt History, write a "
             "list of number ids for the prompts."
             "Be very harsh only include a message from the history if it DIRECTLY relates to the user message, "
             "Otherwise include NOTHING. "
             "Just the list of numbers in square brackets, no commentary",
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
            logging.exception(f"Failed to Retrieve relevant history!")

        return relevant_history
