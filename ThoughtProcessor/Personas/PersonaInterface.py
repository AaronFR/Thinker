import logging
from typing import List, Dict

from ThoughtProcessor.AiWrapper import AiWrapper


class PersonaInterface:
    def __init__(self, name):
        self.name = name

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
    def invalid_function_output(executive_plan: Dict[str, object]) -> bool:
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
