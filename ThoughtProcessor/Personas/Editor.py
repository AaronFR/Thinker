import logging
import os
from pprint import pformat
from typing import Dict, List

from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Personas import PersonaConstants
from ThoughtProcessor.Personas.PersonaInterface import PersonaInterface
from ThoughtProcessor.TaskType import TaskType
from Utility import Utility


class Editor(PersonaInterface):

    def __init__(self, name):
        super().__init__(name)
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")
        self.files_for_evaluation = []
        self.current_thought_id = 1  # self.get_next_thought_id()

        ErrorHandler.setup_logging()

    def work(self, current_task: str):
        """Planner-specific task execution logic
        """
        # ToDo: furnish the execution_logs with more detail and steps
        execution_logs = "Editor editing'...\n"
        self.files_for_evaluation = FileManagement.list_files(str(self.current_thought_id))

        executive_output_dict = self.generate_executive_plan(current_task)
        execution_logs += "EXEC PLAN: " + str(pformat(executive_output_dict)) + "\n"
        # ToDo: create function that checks dicts against function definitions, if a deviation is detected the executive is re-run

        logging.info(f"Generated tasks: {pformat(executive_output_dict.get('tasks'))}")

        tasks = executive_output_dict.get('tasks', [])
        for task in tasks:
            try:
                self.run_task(task)
            except Exception as e:
                failed_task = task.get('what_to_do')
                logging.error(f"Task failed: {failed_task}: {e}")
                execution_logs += f"Task failed: {failed_task}\n"
                FileManagement.save_file(
                    execution_logs,
                    os.path.join(self.thoughts_folder, str(self.current_thought_id), "execution_logs.txt"),
                    str(self.current_thought_id)
                )

    @staticmethod
    def run_task(task_directives: Dict[str, object]):
        logging.info(f"Executing task: \n{pformat(task_directives)}")
        logging.debug("Type input 'bug': = " + str(type(task_directives.get('what_to_do'))))

        logging.info(f"Processing Task: [{task_directives.get('type', TaskType.REWRITE_FILE.value)}]"
                     + str(task_directives.get('what_to_do')))
        executor_thought = PersonaInterface.create_ai_wrapper(task_directives.get('what_to_reference', []))

        thought_type = TaskType(task_directives.get('type', TaskType.REWRITE_FILE.value))
        thought_type.execute(executor_thought, task_directives)
        logging.info(f"Task processed and saved to {task_directives.get('where_to_do_it')}.")

    def generate_executive_plan(self, task: str, additional_user_messages: List[str] = None) -> Dict[str, object]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :param additional_user_messages: any additional information to add before the primary instruction
        :return: A dictionary parsed from the LLM's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        if additional_user_messages:
            Utility.ensure_string_list(additional_user_messages)
        else:
            additional_user_messages = []

        executive_planner = self.create_ai_wrapper(self.files_for_evaluation)

        existing_files = f"Existing files: [{', '.join(str(file) for file in self.files_for_evaluation)}]"
        executive_plan = executive_planner.execute_function(
            [existing_files, PersonaConstants.EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS],
            additional_user_messages + [task],
            PersonaConstants.EDITOR_FUNCTION_SCHEMA
        )

        if not self.valid_function_output(executive_plan):
            logging.info("INVALID SCHEMA, RETRYING...")
            executive_plan = executive_planner.execute_function(
                [existing_files, PersonaConstants.EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS],
                additional_user_messages + [task],
                PersonaConstants.EDITOR_FUNCTION_SCHEMA
            )

            if not self.valid_function_output(executive_plan):
                logging.error("2ND INVALID SCHEMA PRODUCED")

        return executive_plan



if __name__ == '__main__':
    editor = Editor("test")
    editor.work("""Review the translated report for structural coherence according to Dutch reporting styles. 
    Organize the information with clear headings and sections, including an inleiding (introduction) and conclusie (conclusion). 
    Ensure that the formatting aligns with typical Dutch standards for academic or historical reports.
    """)
