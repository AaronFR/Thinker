import logging
from typing import List, Dict

from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.Personas import PersonaConstants


class PersonaInterface:
    def __init__(self, name):
        self.name = name

        ErrorHandler.setup_logging()

    def work(self, task):
        raise NotImplementedError("This method should be overridden by subclasses")

    @staticmethod
    def create_ai_wrapper(input_data: List[str]) -> AiWrapper:
        """
        Create a new wrapper instance for llm processing.

        :param input_data: file references to be used as context.
        :return: An instance of the ai wrapper class.
        """
        # Central management of thought instances
        return AiWrapper(input_data)

    @staticmethod
    def valid_function_output(executive_plan: Dict[str, object]) -> bool:
        """
        Validate the structure and content of a task.
        # ToDo: may need to be spun out as multiple roles with differing schema's are created

        :param executive_plan: A dictionary containing task information.
        :return: True if the task is valid, False otherwise.
        """
        required_keys = ['type', 'what_to_reference', 'what_to_do', 'where_to_do_it']
        tasks = executive_plan.get('tasks')
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
            function_schema: str
        ) -> Dict[str, object]:

        existing_files = f"Existing files: [{', '.join(str(file) for file in files_for_evaluation)}]"
        ai_wrapper = PersonaInterface.create_ai_wrapper(files_for_evaluation)
        executive_plan = ai_wrapper.execute_function(
            [existing_files, function_instructions], additional_user_messages + [task], function_schema
        )

        if not PersonaInterface.valid_function_output(executive_plan):
            logging.info("INVALID SCHEMA, RETRYING...")
            executive_plan = ai_wrapper.execute_function(
                [existing_files, function_instructions], additional_user_messages + [task], function_schema
            )

            if not PersonaInterface.valid_function_output(executive_plan):
                logging.error("2ND INVALID SCHEMA PRODUCED")
                raise Exception("SCHEMA FAILURE")

            return executive_plan
        else:
            return executive_plan
