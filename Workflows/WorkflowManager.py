import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value
from Data.Configuration import Configuration
from Functionality.Coding import Coding
from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA
from Utilities.Decorators import return_for_error
from Utilities.ErrorHandler import ErrorHandler
from Utilities.UserContext import get_user_context


class WorkflowManager:
    """
    Manages the execution of workflows for personas.

    :ivar workflows: A dictionary mapping workflow names to their corresponding functions.
    """

    def __init__(self):
        """
        Initializes the WorkflowManager with an empty workflows dictionary and sets up logging.
        """
        self.workflows: Dict[str, Callable] = {}

        self.register_workflow("chat", self.chat_workflow)
        self.register_workflow("write", self.write_workflow)
        self.register_workflow("write_tests", self.write_tests_workflow)
        ErrorHandler.setup_logging()

    def register_workflow(self, name: str, workflow_func: Callable):
        """
        Registers a new workflow function.

        :param name: Name of the workflow.
        :param workflow_func: Workflow function to register.
        """
        self.workflows[name] = workflow_func
        logging.info(f"Workflow '{name}' registered.")

    def execute_workflow(self, name: str, *args, **kwargs):
        """
        Executes the specified workflow.

        :param name: Name of the workflow.
        :param args: Positional arguments for the workflow.
        :param kwargs: Keyword arguments for the workflow.
        :return: The result of the workflow execution.
        :raises ValueError: If the workflow does not exist.
        """
        if name not in self.workflows:
            logging.error(f"Workflow '{name}' not found.")
            raise ValueError(f"Workflow {name} not found.")
        logging.info(f"Executing workflow '{name}'.")
        return self.workflows[name](*args, **kwargs)

    @return_for_error("An error occurred during the chat workflow.", debug_logging=True)
    def chat_workflow(
        self,
        process_question: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Converses with the user

        :param process_question: Function for the selected persona to process the user's question.
        :param initial_message: The user's initial prompt.
        :param file_references: References to files related to the query.
        :param selected_message_ids: References to prior prompt/responses related to the query.
        :param tags: Additional metadata affecting the workflow including category and model.
         If no model is supplied a default will be chosen
        :return: Processed response from the workflow.
        """
        logging.info("Chat workflow selected")
        analyser_messages = [
            initial_message
        ]
        prompt_messages = analyser_messages
        model = find_enum_value(tags.get("model"))

        for iteration, message in enumerate(prompt_messages, start=1):
            response = process_question(
                message,
                file_references,
                selected_message_ids,
                streaming=True,
                model=model
            )
            logging.info("Iteration %d completed", iteration)

        return response

    @return_for_error("An error occurred during the write workflow.", debug_logging=True)
    def write_workflow(
        self,
        process_question: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Writes code based on the user's specifications.

        :param process_question: Function to process the user's question.
        :param initial_message: The user's guidance for writing code.
        :param file_references: References to files that might be involved.
        :param selected_message_ids: Context message IDs.
        :param tags: Additional information influencing the writing process.
        :return: Processed response from the workflow.
        """
        executor = AiOrchestrator()
        config = Configuration.load_config()
        model = find_enum_value(tags.get("model"))

        if tags and tags.get("write"):
            files = [{
                "file_name": tags.get("write"),
                "purpose": "create from scratch"
            }]
        else:
            prompt = (
                "Give just a filename (with extension) that should be worked on given the following prompt. "
                "No commentary. "
                "If appropriate, write multiple files, the ones at the top of the class hierarchy first/on the top."
            ) if config['beta_features']['multi_file_processing_enabled'] else (
                "Give just a filename (with extension) that should be worked on given the following prompt. "
                "No commentary. Select only one singular file alone."
            )

            files = executor.execute_function(
                [prompt],
                [initial_message],
                GENERATE_FILE_NAMES_FUNCTION_SCHEMA
            )['files']

        logging.info(f"Referencing/Creating the following files: {files}")

        for file in files:
            file_name = file['file_name']
            user_id = get_user_context()
            file_path = Path(user_id).joinpath(file_name)

            purpose = file['purpose']
            logging.info(f"Writing code to {file_path}, \nPurpose: {purpose}")

            if Coding.is_coding_file(file_name):
                step_two = (
                    f"Write/Rewrite {file_name} based on your previous plan of action and the actual contents of "
                    f"this particular file, focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
                    "Making sure that the file imports as necessary, referencing the appropriate classes. "
                    "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
                    "Unless explicitly requested, the file's content must be preserved by default."
                )
            else:
                step_two = (
                    f"Write/Rewrite {file_name} based on your previous plan of action for this particular file, "
                    f"focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
                    "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
                    "Unless explicitly requested, the file's content must be preserved by default."
                )

            analyser_messages = [
                f"<user_prompt>{initial_message}</user_prompt>: to start with we will narrow our focus on {file_name} "
                "and think through how to change it/write it so as to fulfill the user prompt, step by step, discussing"
                " what we know, identify specifically what they want accomplished, goals and sub-goals, "
                f"and any existing flaws or defects WITHOUT writing any text or code for {file_name}. "
                "Just writing up a plan of action telling the LLM to follow how to rewrite/write the file in line with "
                "this plan and stating specifically that this plan is to be replaced with actual functioning file.",

                step_two,

                "Very quickly summarize what you just wrote and where you wrote it."
            ]
            prompt_messages = analyser_messages

            for iteration, message in enumerate(prompt_messages, start=1):
                if iteration == 1:
                    response = process_question(
                        message,
                        file_references
                    )
                    logging.info("Iteration %d completed with response: %s", iteration, response)

                if iteration == 2:
                    response = process_question(
                        message,
                        file_references,
                        model=model
                    )
                    logging.info("Iteration %d completed with response: %s", iteration, response)

                    Coding.write_to_file_task({
                        PersonaConstants.SAVE_TO: file_path,
                        PersonaConstants.INSTRUCTION: response
                    })

                if iteration == 3:
                    response = process_question(
                        message,
                        file_references,
                        selected_message_ids,
                        streaming=True
                    )
                    logging.info("Iteration %d completed, streaming workflow completion summary", iteration)

        return response

    @return_for_error("An error occurred during the write tests workflow.", debug_logging=True)
    def write_tests_workflow(
        self,
        process_question: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generates a test file for a specified file.

        :param process_question: Function to process the user's question.
        :param initial_message: The user's guidance for writing tests.
        :param file_references: References to files related to the tests.
        :param selected_message_ids: Message IDs for context.
        :param tags: Additional metadata affecting the workflow.
        :return: Processed response from the workflow.
        """
        model = find_enum_value(tags.get("model"))

        executor = AiOrchestrator()
        file_name = executor.execute(
            ["Please provide the filename (including extension) of the code for which tests should be written. "
             "Please be concise."],
            [initial_message]
        )

        test_prompt_messages = [
            f"Review {file_name} in light of [{initial_message}]. What should we test? How? What should we prioritize "
            f"and how should the test file be structured?",

            f"Write a test file for {file_name}, implementing the tests as we discussed. Make sure each test has robust"
            " documentation explaining the test's purpose.",

            f"Assess edge cases and boundary conditions in {file_name}, generating appropriate tests. "
            f"Present the final test cases in {file_name} and comment on coverage and areas needing additional tests.",

            "Very quickly summarize the tests you just wrote and what specifically they aim to test."
        ]
        prompt_messages = test_prompt_messages

        for iteration, message in enumerate(prompt_messages, start=1):
            if iteration == 1:
                response = process_question(
                    message,
                    file_references
                )
                logging.info("Test Workflow Iteration %d completed with response: %s", iteration, response)

                # Save the tests
                Coding.write_to_file_task({
                    "save_to": file_name,
                    "instruction": response
                })

            if iteration == 2:
                response = process_question(
                    message,
                    file_references,
                    selected_message_ids,
                    streaming=True,
                    model=model
                )
                logging.info("Test Workflow Iteration %d completed, streaming workflow completion summary", iteration)

        return response
