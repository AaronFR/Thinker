import logging
import os
from pprint import pformat
from typing import Dict, List

import Constants
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.AiWrapper import AiWrapper
from ThoughtProcessor.TaskType import TaskType
from ThoughtProcessor.FileManagement import FileManagement

class TaskRunner:
    def __init__(self, current_thought_id: int, prompter, open_ai_client):
        self.current_thought_id = current_thought_id
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "Thoughts")
        self.prompter = prompter
        self.open_ai_client = open_ai_client

        ErrorHandler.setup_logging()

    def run_iteration(self, current_task: str, attempt_count: int):
        """
        Orchestrate the execution of tasks based on the current user prompt.
        ToDo: implement system for dealing with failed tasks

        :param current_task: the current initial user prompt to work on
        :param attempt_count: number of iterations the user prompt has been worked on
        :return:
        """
        execution_logs = ""
        current_prompt_folder = os.path.join(self.thoughts_folder, f"{self.current_thought_id}")
        self.files_for_evaluation = FileManagement.list_files(current_prompt_folder)

        executive_output_dict = self.generate_executive_plan(current_task)
        execution_logs += "EXEC PLAN: " + str(pformat(executive_output_dict)) + "\n"

        if executive_output_dict.get('solved'):
            logging.info(f"Task `{current_task}` solved successfully in attempt {attempt_count}.")
            self.finalise_solution(self.current_thought_id, execution_logs)
            return True  # Exit if the solution is found

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
                    "1"
                )

        return False

    def run_task(self, task_directives: Dict[str, object]):
        logging.info(f"Executing task: \n{pformat(task_directives)}")
        logging.debug("Type input 'bug': = " + str(type(task_directives.get('what_to_do'))))

        logging.info(f"Processing Task: [{task_directives.get('type', TaskType.APPEND.value)}]"
                     + str(task_directives.get('what_to_do')))
        executor_thought = self.generate_ai_wrapper(task_directives.get('what_to_reference', []))

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
        executive_output = executive_thought.executive_think(
            [existing_files, Constants.EXECUTIVE_FUNCTION_INSTRUCTIONS], task)

        return executive_output

    def generate_ai_wrapper(self, input_data: List[str]) -> AiWrapper:
        """
        Create a new wrapper instance for llm processing.

        :param input_data: file references to be used as context.
        :return: An instance of the ai wrapper class.
        """
        # Central management of thought instances
        return AiWrapper(input_data, self.prompter, self.open_ai_client)

    def finalise_solution(self, iteration: int, logs: str) -> None:
        """
        Finalize and save the logs, after successful evaluation of the solution.

        :param iteration: The iteration number where a solution was found.
        :param logs: The logs generated during the evaluation process.
        """
        logging.info(f"Solved by iteration: {iteration}")
        FileManagement.save_file(logs, os.path.join(self.thoughts_folder, str(self.current_thought_id), "logs.txt"), "")
