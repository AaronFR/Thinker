import logging
from pprint import pformat
from typing import Dict, List

import Globals
from ExecutionLogs import ExecutionLogs
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Personas import PersonaConstants
from ThoughtProcessor.Personas.BasePersona import BasePersona
from ThoughtProcessor.TaskType import TaskType
from Utility import Utility


class Editor(BasePersona):

    def __init__(self, name):
        super().__init__(name)
        self.files_for_evaluation = []

        ErrorHandler.setup_logging()

    def work(self, current_task: str):
        """Planner-specific task execution logic
        """
        self.files_for_evaluation = FileManagement.list_files(str(Globals.thought_id))

        executive_output_dict = self.generate_executive_plan(current_task)

        logging.info(f"Generated tasks: {pformat(executive_output_dict.get('tasks'), width=280)}")
        ExecutionLogs.add_to_logs(f"Generated tasks: {pformat(executive_output_dict.get('tasks'), width=280)}")

        tasks = executive_output_dict.get('tasks', [])
        for task in tasks:
            self._process_task(task)

    @staticmethod
    def run_task(task_directives: Dict[str, object]):
        ExecutionLogs.add_to_logs(f"Executing task: \n{pformat(task_directives)}")
        executor_thought = BasePersona.create_ai_wrapper(task_directives.get('what_to_reference', []))

        thought_type = TaskType(task_directives.get('type', TaskType.REWRITE_FILE.value))
        thought_type.execute(executor_thought, task_directives)

    def generate_executive_plan(self, task: str, additional_user_messages: List[str] = None) -> Dict[str, object]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :param additional_user_messages: any additional information to add before the primary instruction
        :return: A dictionary parsed from the LLM's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        additional_user_messages = additional_user_messages or []
        if additional_user_messages:
            Utility.ensure_string_list(additional_user_messages)

        return self.generate_function(
            self.files_for_evaluation,
            additional_user_messages,
            task,
            PersonaConstants.EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS,
            PersonaConstants.EDITOR_FUNCTION_SCHEMA
        )


if __name__ == '__main__':
    editor = Editor("test")
    editor.work("""Review the translated report for structural coherence according to Dutch reporting styles. 
    Organize the information with clear headings and sections, including an inleiding (introduction) and conclusie (conclusion). 
    Ensure that the formatting aligns with typical Dutch standards for academic or historical reports.
    """)
