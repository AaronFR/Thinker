import logging
from pprint import pformat
from typing import Dict, List

from Functionality.Writing import Writing
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.ErrorHandler import ErrorHandler
from Utilities.FileManagement import FileManagement
from Personas.PersonaSpecification import PersonaConstants
from Personas.BasePersona import BasePersona
from Utilities.Utility import Utility


class Writer(BasePersona):
    """Writer persona, representing a role that manages writing tasks and their outputs
    """

    writing_tasks = [Writing.WRITE, Writing.APPEND]

    def __init__(self, name):
        super().__init__(name)
        self.evaluation_files = []

        ErrorHandler.setup_logging()

    def execute_task(self, task_to_execute: str):
        """Executes the specified writing task.

        This method is responsible for managing the execution of a writing task by first retrieving
        the evaluation files, then generating an executive plan based on the given task, and
        finally processing the individual tasks outlined in that plan.

        :param: task_to_execute (str): The writing task that needs to be executed.
        """
        self.evaluation_files = FileManagement.list_file_names()

        executive_plan = self.generate_executive_plan(task_to_execute)

        ExecutionLogs.add_to_logs(f"Initiating task processing. Current task: {task_to_execute}")
        logging.info(f"Generated tasks: {pformat(executive_plan[PersonaConstants.TASKS], width=280)}")
        ExecutionLogs.add_to_logs(f"Generated tasks: {pformat(executive_plan[PersonaConstants.TASKS], width=280)}")

        tasks = executive_plan.get(PersonaConstants.TASKS, [])
        for task in tasks:
            self._process_task(task)

    @staticmethod
    def execute_task_parameters(task_parameters: Dict[str, object]):
        """Executes a writing task based on provided parameters.

        This method retrieves the task type from the given parameters and attempts to execute
        the corresponding writing task.

        :param task_parameters: A dictionary containing the parameters for the writing task,
                               including the task type and other relevant details.
        :raises ValueError: If the task type specified in the parameters is invalid or
                            not supported by this persona.
        """
        ExecutionLogs.add_to_logs(f"Executing task: \n{pformat(task_parameters)}")

        writing_task = Writing(task_parameters.get(PersonaConstants.TYPE, Writing.APPEND.value))
        if writing_task in Writer.writing_tasks:
            writing_task.execute(task_parameters)
        else:
            raise ValueError("Invalid task type used for this persona")

    def generate_executive_plan(self, task: str, extra_user_inputs: List[str] = None) -> Dict[str, object]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :param extra_user_inputs: any additional information to add before the primary instruction
        :return: A dictionary parsed from the LLM's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        extra_user_inputs = extra_user_inputs or []
        if extra_user_inputs:
            Utility.ensure_string_list(extra_user_inputs)

        return self.generate_function(
            self.evaluation_files,
            extra_user_inputs,
            task,
            PersonaConstants.EXECUTIVE_WRITER_FUNCTION_INSTRUCTIONS,
            PersonaConstants.WRITER_FUNCTION_SCHEMA
        )


if __name__ == '__main__':
    writer = Writer("test")
    writer.execute_task("""Write a detailed report about the future of tidal technology, what innovations and possible disruptions could occur
    """)
