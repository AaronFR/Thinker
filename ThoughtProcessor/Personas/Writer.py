import logging
import os
from pprint import pformat
from typing import Dict, List

from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Personas import Persona_Constants
from ThoughtProcessor.Personas.PersonaInterface import PersonaInterface
from ThoughtProcessor.TaskType import TaskType


class Writer(PersonaInterface):

    def __init__(self, name):
        super().__init__(name)
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")
        self.files_for_evaluation = []
        self.current_thought_id = 1  # self.get_next_thought_id()

        ErrorHandler.setup_logging()

    def work(self, current_task: str):
        """Planner-specific task execution logic
        """
        execution_logs = ""
        self.files_for_evaluation = FileManagement.list_files(str(self.current_thought_id))

        # ToDo: re-write schema splitting out writer specific version
        executive_output_dict = self.generate_executive_plan(current_task)
        execution_logs += "EXEC PLAN: " + str(pformat(executive_output_dict)) + "\n"
        # ToDo: add task  method that WRITES a full file to a specified length: 2000 tokens * n iterations
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

        logging.info(f"Processing Task: [{task_directives.get('type', TaskType.APPEND.value)}]"
                     + str(task_directives.get('what_to_do')))
        executor_thought = Writer.generate_ai_wrapper(task_directives.get('what_to_reference', []))

        thought_type = TaskType(task_directives.get('type', TaskType.APPEND.value))
        thought_type.execute(executor_thought, task_directives)
        logging.info(f"Task processed and saved to {task_directives.get('where_to_do_it')}.")

    def generate_executive_plan(self, task: str) -> Dict[str, object]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :return: A dictionary parsed from the llm's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        executive_thought = self.generate_ai_wrapper(self.files_for_evaluation)
        existing_files = f"Existing files: [{', '.join(str(file) for file in self.files_for_evaluation)}]"
        executive_output = executive_thought.execute_function(
            [existing_files, Persona_Constants.EXECUTIVE_WRITER_FUNCTION_INSTRUCTIONS],
            task,
            Persona_Constants.WRITER_FUNCTION_SCHEMA
        )

        return executive_output

    @staticmethod
    def generate_ai_wrapper(input_data: List[str]) -> AiWrapper:
        """
        Create a new wrapper instance for llm processing.

        :param input_data: file references to be used as context.
        :return: An instance of the ai wrapper class.
        """
        # Central management of thought instances
        return AiWrapper(input_data)
