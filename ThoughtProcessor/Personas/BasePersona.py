import logging
import time
from typing import List, Dict

import Constants
from ThoughtProcessor.ExecutionLogs import ExecutionLogs
from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.Personas import PersonaConstants
from Utility import Utility


class BasePersona:
    """
    Base class for creating personas that execute tasks.

    Subclasses must implement the following methods:
    - execute_task(task): Define how the persona performs a specific task.
    - execute_task_directives(task_directives): Execute specific instructions contained in the task directives.
    """

    def __init__(self, name):
        self.name = name

        ErrorHandler.setup_logging()

    def execute_task(self, task):
        """
        Execute a given task.

        :param task: A dictionary containing details of the task to be performed.
        Raises: NotImplementedError: If not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    @staticmethod
    def execute_task_directives(task_directives: Dict[str, object]):
        """
        Execute instructions contained in task directives.

        :param task_directives: A dictionary containing directives for task execution.
        Raises: NotImplementedError: If not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _process_task(self, task: Dict[str, object]):
        """
        Processes a task and handles any exceptions that occur during execution.

        :param task: A dictionary containing task information.
        """
        try:
            self.execute_task_directives(task)
        except Exception:
            failed_task = task.get('what_to_do')
            logging.exception(f"Task failed: {failed_task}")
            ExecutionLogs.add_to_logs(f"Task failed: {failed_task}\n")

    @staticmethod
    def create_ai_wrapper(input_data: List[str]) -> AiWrapper:
        """
        Create a new wrapper instance for llm processing.

        :param input_data: file references to be used as context.
        :return: An instance of the AI wrapper class.
        """
        return AiWrapper(input_data)

    @staticmethod
    def valid_function_output(
            executive_plan: Dict[str, object],
            required_keys: List[str] = PersonaConstants.DEFAULT_REQUIRED_KEYS) -> bool:
        """
        Validate the structure and content of a task.

        :param executive_plan: A dictionary containing task information.
        :param required_keys: the necessary keys for a Dict to be evaluated as valid
        :return: True if the task is valid, False otherwise.
        """
        tasks = executive_plan.get(PersonaConstants.TASKS)
        for task in tasks:
            for key in required_keys:
                if key not in task:
                    logging.error(f"Missing required key: {key} in task: {task}")
                    return False

        logging.info(f"Task validated successfully: {executive_plan}")
        return True

    @staticmethod
    def generate_function(
            files_for_evaluation: List[str],
            additional_user_messages: List[str],
            task: str,
            function_instructions: str,
            function_schema: str,
            max_retries: int = Constants.MAX_SCHEMA_RETRIES) -> Dict[str, object]:
        """
        Generate a function based on provided evaluation files and instructions.

        Executes an LLM function to evaluate the provided files and returns an
        executive plan. Includes a maximum retry mechanism with exponential backoff
        for failure cases.

        :param files_for_evaluation: List of file paths to be evaluated.
        :param additional_user_messages: Any additional messages to provide context.
        :param task: The main task to be performed.
        :param function_instructions: Instructions on how to perform the function.
        :param function_schema: Schema that the function output must adhere to.
        :param max_retries: Maximum number of retries for generating a valid executive plan.
        :return: A dictionary representing the executive plan generated by the LLM.
        :raises Exception: If the generated output does not conform to the expected schema after retries.
        """

        existing_files = f"Existing files: [{', '.join(str(file) for file in files_for_evaluation)}]"
        ai_wrapper = BasePersona.create_ai_wrapper(files_for_evaluation)

        for attempt in range(max_retries + 1):
            executive_plan = ai_wrapper.execute_function(
                [existing_files, function_instructions],
                additional_user_messages + [task],
                function_schema
            )

            if BasePersona.valid_function_output(executive_plan):
                return executive_plan

            else:
                logging.error("Exceeded maximum retries for generating a valid executive plan.")
                raise Exception("SCHEMA FAILURE after maximum retries")
