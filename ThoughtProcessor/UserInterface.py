import logging
import os
from collections import deque

import Constants
import Globals
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.TaskRunner import PersonaSystem


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
        self.task_runner = PersonaSystem()

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
        if not self.validate_prompt(user_prompt):
            return  # Exit early on invalid input

        current_prompt_folder = os.path.join(FileManagement.thoughts_folder, f"{Globals.thought_id}")
        os.makedirs(current_prompt_folder, exist_ok=True)

        task_queue = deque([user_prompt])  # Main task queue
        Globals.workers = []

        while task_queue:
            current_task = task_queue.popleft()  # Get the next task
            attempt_count = 0  # Reset attempt counter for the current task

            # Iterate through execution attempts for a given task
            while self.within_budget():
                if attempt_count >= self.MAX_TRIES:
                    self._log_and_save_unsolved_problem()
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

            self._log_process_completion(current_task, attempt_count)

    def validate_prompt(self, user_prompt: str) -> bool:
        """Validate user input prompt
        Later will need to include content moderation

        """
        if user_prompt is None or not user_prompt.strip():
            logging.error("Invalid input: user_prompt cannot be None or empty.")
            return False
        return True

    def _log_and_save_unsolved_problem(self):
        """Log and save information about an unsolved problem."""
        logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.MAX_TRIES} ATTEMPTS")
        execution_logs = f"PROBLEM REMAINS UNSOLVED AFTER {self.MAX_TRIES} ATTEMPTS\n"
        FileManagement.save_file(execution_logs, Constants.execution_logs_filename)

    @staticmethod
    def _log_process_completion(current_task: str, attempt_count: int):
        """Log the termination of a request process"""
        logging.info(f"""FINISHED REQUEST: [{current_task}]
                        in {attempt_count} iterations
                        total cost: ${round(Globals.current_request_cost, 4)}""")
        Globals.current_request_cost = 0.0

    @staticmethod
    def within_budget(budget: float = BUDGET) -> bool:
        """
        Check if the current cost is within the budget.

        :param budget: The budget limit.
        :return: True if within budget, False otherwise.
        """
        logging.info(
            f"""Current cost: ${round(Globals.current_request_cost, 5)}, {round((Globals.current_request_cost / budget) * 100, 5)}%""")
        return Globals.current_request_cost <= budget


if __name__ == '__main__':
    thought_process = UserInterface()

    thought_process.evaluate_prompt(
        """Make suggestions in a report markdown file on how to improve UserInterface.py, with 
        (consise small individual) examples.
        Demonstrate to specifically rather than theoretically how the class can be improved"""
    )
