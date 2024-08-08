import logging
import os
from collections import deque

import Constants
import Globals
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
        files_for_evaluation (list): List of files to be evaluated.
        max_tries (int): Maximum attempts allowed to resolve a task.
    """

    MAX_TRIES = 15
    BUDGET = 0.01  # $

    def __init__(self):
        """
        Initialize the UserInterface instance.
        """
        self.files_for_evaluation = []
        self.task_runner = TaskRunner()

        ErrorHandler.setup_logging()

    def evaluate_prompt(self, user_prompt: str):
        """
        Evaluate and execute a task based on its description.

        This method coordinates the assessment and execution process, generating execution plans,
        attempting the resolution iteratively, and keeping logs of performance outcomes.

        The method tries to solve the provided task by executing iterations within a budget limit.

        :param user_prompt: The description of the task to evaluate as a string. This should be
                           a concise prompt that describes the desired outcome, such as a
                           question or request

        Returns:
            None: This method does not return a value. It logs the process and updates the system state.
        """
        current_prompt_folder = os.path.join(FileManagement.thoughts_folder, f"{Globals.thought_id}")
        os.makedirs(current_prompt_folder, exist_ok=True)

        task_queue = deque([user_prompt])  # Main task queue
        Globals.workers = []

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
                    if Globals.workers:
                        worker = Globals.workers.pop()
                        solved = self.task_runner.run_iteration(worker.get('instructions'), worker.get('type'))
                    else:
                        solved = self.task_runner.run_iteration(current_task)

                    if solved:
                        logging.info("TASK SOLVED")
                        return
                except Exception as e:
                    logging.error(f"Error processing executive thought for `{current_task}`: {e}")
                    break  # Exit loop on processing executive thought failure

                attempt_count += 1

            logging.info(f"""FINISHED REQUEST: [{current_task}]\nin {attempt_count} iterations
                         \ntotal cost: ${round(Globals.request_price, 4)}""")
            Globals.request_price = 0.0

    @staticmethod
    def within_budget(budget=0.01):
        logging.info(f"Current cost: ${round(Globals.request_price, 5)}")
        return Globals.request_price <= budget


if __name__ == '__main__':
    thought_process = UserInterface()

    thought_process.evaluate_prompt(
        """Make suggestions in a report markdown file on how to improve UserInterface.py, with 
        (consise small individual) examples.
        Demonstrate to specifically rather than theoretically how the class can be improved"""
    )
