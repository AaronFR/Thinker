import logging
import os
from collections import deque

from openai import OpenAI

import Constants
from Prompter import Prompter
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.TaskRunner import TaskRunner


class UserInterface:
    """
    Handles user input tasks for processing by the iterative system

    The UserInterface orchestrates the flow of task evaluation by breaking user prompts down into actionable
    chunks. The process includes multiple retries for task execution, allowing
    the system to address and resolve complex problems iteratively.

    Attributes:
        thoughts_folder (str): Directory where thoughts are stored.
        files_for_evaluation (list): List of files available for evaluation.
        current_thought_id (int): Unique identifier for the current thought process.
        prompter (Prompter): An instance to manage prompts for task communication.
        open_ai_client (OpenAI): Client for interaction with the OpenAI API.
        max_tries (int): Maximum attempts to resolve a task.
    """

    def __init__(self):
        """
        Initialize the ThoughtProcess instance.
        """
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "Thoughts")
        self.files_for_evaluation = []
        self.current_thought_id = 1  # self.get_next_thought_id()

        self.prompter = Prompter()
        self.open_ai_client = OpenAI()
        self.task_runner = TaskRunner(self.current_thought_id, self.prompter, self.open_ai_client)
        self.max_tries = 15

        ErrorHandler.setup_logging()

    def evaluate_prompt(self, user_prompt: str):
        """
        Evaluate and execute a task based on its description.

        This method coordinates the assessment and execution process, generating execution plans,
        attempting the resolution iteratively, and keeping logs of performance outcomes.

        :param user_prompt: The description of the task to evaluate as a string.
        """
        current_prompt_folder = os.path.join(self.thoughts_folder, f"{self.current_thought_id}")
        os.makedirs(current_prompt_folder, exist_ok=True)

        task_queue = deque([user_prompt])  # Main task queue

        while task_queue:
            current_task = task_queue.popleft()  # Get the next task
            attempt_count = 0  # Reset attempt counter for the current task

            # Iterate through execution attempts for a given task
            while self.within_budget():
                if attempt_count == self.max_tries:
                    logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
                    execution_logs = f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS\n"  # Capture final attempt logs
                    FileManagement.save_file(
                        execution_logs,
                        os.path.join(self.thoughts_folder, str(self.current_thought_id), "execution_logs.txt"),
                        ""
                    )
                    break

                try:
                    solved = self.task_runner.run_iteration(current_task, attempt_count)
                    if solved:
                        return
                except Exception as e:
                    logging.error(f"Error processing executive thought for `{current_task}`: {e}")
                    break  # Exit loop on processing executive thought failure

                attempt_count += 1

            logging.info(f"FINISHED REQUEST: [{current_task}]\nin {attempt_count} iterations\ntotal cost: {Constants.request_price}")
            Constants.request_price = 0.0

    @staticmethod
    def within_budget(budget=0.01):
        logging.info(f"Current cost: {Constants.request_price}")
        return Constants.request_price <= budget


if __name__ == '__main__':
    thought_process = UserInterface()

    thought_process.evaluate_prompt(
        """Write your suggestions on how to improve TaskRunner.py in a separate markdown file called 'suggestions.md
        do not edit the original file in any way, tailor your review around logical architecutral improvements
        specific lines of code that could be refactored to be more intuitive, performant, etc.
        These types of practical concerns. Don't suggest logging changes, unit tests or exceptions'"""
    )

