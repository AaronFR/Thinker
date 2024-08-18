import logging
from pprint import pformat
from typing import Dict, List

from Functionality.Writing import Writing
from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.EditorSpecification import EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS, \
    EDITOR_EXECUTIVE_FUNCTION_SCHEMA
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.ErrorHandler import ErrorHandler
from Utilities.FileManagement import FileManagement
from Personas.PersonaSpecification.PersonaConstants import TASKS, TYPE
from Personas.BasePersona import BasePersona
from Utilities.Utility import Utility


class Editor(BasePersona):
    """
    Editor persona is responsible for editorialising: reviewing an existing document and making substitutions and
    amendments.
    """
    writing_tasks = [Writing.REWRITE, Writing.REWRITE_FILE, Writing.REGEX_REFACTOR]

    def __init__(self, name):
        super().__init__(name)
        self.evaluation_files = []

        ErrorHandler.setup_logging()

    def execute_task(self, task_to_execute: str):
        """
        Planner-specific task execution logic.

        :param task_to_execute: The task to be executed.
        :raises ValueError: If the task_to_execute is empty or invalid.
        :raises Exception: If an error occurs during task execution.
        """
        self.evaluation_files = FileManagement.list_file_names()

        executive_plan = self.generate_executive_plan(task_to_execute)

        logging.info(f"Generated tasks: {pformat(executive_plan[TASKS], width=280)}")
        ExecutionLogs.add_to_logs(f"Generated tasks: {pformat(executive_plan[TASKS], width=280)}")

        tasks = executive_plan[TASKS]
        for task in tasks:
            self._process_task(task)

    @staticmethod
    def execute_task_parameters(task_parameters: Dict[str, object]):
        ExecutionLogs.add_to_logs(f"Executing task: \n{pformat(task_parameters)}")

        writing_task = Writing(task_parameters.get(PersonaConstants.TYPE, Writing.REWRITE_FILE.value))
        if writing_task in Editor.writing_tasks:
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
            EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS,
            EDITOR_EXECUTIVE_FUNCTION_SCHEMA
        )


if __name__ == '__main__':
    editor = Editor("test")
    # editor.execute_task("""Review the translated report for structural coherence according to Dutch reporting styles.
    #     Organize the information with clear headings and sections, including an inleiding (introduction) and conclusie (conclusion).
    #     Ensure that the formatting aligns with typical Dutch standards for academic or historical reports.""")
    editor.execute_task("""Rewrite the README for generally improved quality and coherency. In particular focus on 
    rewriting the #Features to implement section
    I'm thinking about this section as I reference it often while developing, in particular I think a greater emphassis 
    needs to be put on refining the architecture and improving overall executive thought processes.
    That is processes which govern the implementation of a target solution to a user request, rather than
    the processes which directly improve a given solution under direction from these executive processes.
    Be creative, I'm only taking interesting ideas to influence how **I** update the README.
    """)

