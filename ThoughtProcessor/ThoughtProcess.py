import json
import logging
import os
from typing import List, Dict

from openai import OpenAI

import Constants
from Prompter import Prompter
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Thought import Thought


class ThoughtProcess:
    """
    Class to handle the process of evaluating tasks using the Thought class.
    """

    def __init__(self):
        """
        Initialize the ThoughtProcess instance.

        :param files_to_evaluate: List of file paths supplied by the user as reference against their task.
        """
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "Thoughts")
        self.files_to_evaluate = []
        self.thought_id = 1  # self.get_next_thought_id()
        FileManagement.initialise_file(self.thought_id, "solution.txt")

        self.prompter = Prompter()
        self.open_ai_client = OpenAI()
        self.max_tries = 5

    def get_next_thought_id(self) -> int:
        """
        Get the next available thought ID based on existing directories.

        :return: Next available thought ID as an integer.
        """
        os.makedirs(self.thoughts_folder, exist_ok=True)
        return len([name for name in os.listdir(self.thoughts_folder) if
                    os.path.isdir(os.path.join(self.thoughts_folder, name))]) + 1

    def evaluate_and_execute_task(self, task_description: str):
        """
        Evaluate the given task and attempt to provide an optimized solution.

        This method runs multiple iterations to process the task and saves
        any relevant logs or solutions.

        ToDo: Should probably switch to using a DAG with edges

        :param task_description: The description of the task to evaluate as a string.
        """
        new_folder = os.path.join(self.thoughts_folder, f"{self.thought_id}")
        os.makedirs(new_folder, exist_ok=True)

        logs = ""
        for iteration in range(1, self.max_tries + 1):
            logging.info(f"Starting iteration {iteration} for task: {task_description}")
            self.files_to_evaluate = FileManagement.list_files(new_folder)

            executive_output_dict = self.process_executive_thought(task_description)
            logs += str(executive_output_dict) + "\n"
            if executive_output_dict.get('solved'):
                self.finalise_solution(iteration, logs)
                break

            logging.info(f"About to iterate task list: {executive_output_dict.get('tasks')}")
            tasks = executive_output_dict.get('tasks')
            number_of_tasks = len(tasks)
            for task_number, task in enumerate(tasks):
                logging.info(f"Executing task: {task_number + 1}/{number_of_tasks} : \n{pformat(task)}")
                self.process_thought(task.get('what_to_do'), task.get('what_to_reference'), task.get('where_to_do_it'))
        else:
            logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
            FileManagement.save_file(
                logs,
                os.path.join(self.thoughts_folder, str(self.thought_id), "logs.txt"),
                "",
                True
            )

    def process_executive_thought(self, task: str) -> Dict[str, str]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :return: A dictionary parsed from the llm's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        executive_thought = self.create_next_thought(self.files_to_evaluate)
        executive_output = executive_thought.think([Constants.EXECUTIVE_PROMPT], task)
        try:
            logging.info(f"Converting executive output from json format to dict: \n{executive_output}")
            return json.loads(executive_output)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON output: %s", executive_output)
            raise

    def process_thought(
            self,
            executive_directive: str,
            external_files: List[str],
            save_to: str,
            overwrite: bool = False
        ):
        """
        Process the thoughts generated from the executive output and save results.

        ToDo: Should probably change system_message if its the first iteration

        :param executive_directive: Primary instruction for this task
        :param external_files: List of external files used as context.
        :param save_to: File path where output should be saved.
        :param overwrite: Boolean flag to determine if the output file should be overwritten. ToDo: Not currently in service
        """
        logging.info("Processing Thought: " + executive_directive)
        thought = self.create_next_thought(external_files)
        output = thought.think(
            Constants.PROMPT_FOLLOWING_EXECUTIVE_DIRECTION,
            "Primary Instructions: " + str(executive_directive)
        )
        FileManagement.save_file(output, save_to, str(self.thought_id), overwrite)

    def create_next_thought(self, input_data: List[str]) -> Thought:
        """
        Create a new Thought instance for processing.

        :param input_data: file references to be used as context.
        :return: An instance of the Thought class.
        """
        # Central management of thought instances
        new_thought = Thought(input_data, self.prompter, self.open_ai_client)
        return new_thought

    def finalise_solution(self, iteration: int, logs: str) -> None:
        """
        Finalize and save the logs, after successful evaluation of the solution.

        :param iteration: The iteration number where a solution was found.
        :param logs: The logs generated during the evaluation process.
        """
        logging.info(f"Solved by iteration: {iteration}")
        FileManagement.save_file(logs, os.path.join(self.thoughts_folder, str(self.thought_id), "logs.txt"), "")


if __name__ == '__main__':
    ErrorHandler.setup_logging()
    thought_process = ThoughtProcess()

    thought_process.evaluate_and_execute_task(
        """Review ThoughtProcess.py and make suggestions in a new document suggestions.md as to how I could change the method definitions to be more intuitive to make the flow more understandable, first minor changes then drastic changes"""
    )
    #
    # # Please don't overwrite ThoughtProcess to fill it with theory, it needs to remain a valid python file as it was"""
    # # """Take ThoughtProcess.py and re-write so that method has a docstring. Please don't overwrite ThoughtProcess to fill it with theory, it needs to remain a valid python file as it was"""  # found to overwrite python files in a meaningful way
