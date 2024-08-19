import logging
import os
from collections import deque

from Utilities import Globals
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.ErrorHandler import ErrorHandler
from Utilities.FileManagement import FileManagement
from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSystem import PersonaSystem


class UserInterface:
    """
    Manages user input for processing within the iterative system.

    The UserInterface coordinates task evaluation by decomposing user prompts into manageable components, to be
    iterated upon by a worker or 'Persona' making individual llm calls.

    Attributes:
        evaluation_files (list): List of files to be evaluated.
        MAX_TRIES (int): Maximum attempts allowed to resolve a task.
        BUDGET (float): used budget for calling ai API's
    """

    MAX_TRIES = 5
    BUDGET = 0.01  # $

    def __init__(self):
        """
        Initialize the UserInterface instance and set up logging.
        """
        self.evaluation_files = []
        self.persona_system = PersonaSystem()

        ExecutionLogs.setup_logging()
        ErrorHandler.setup_logging()

    def process_user_prompt(self, user_prompt: str):
        """
        Validate and manage the execution of the user's input prompt.

        Upon validation of user input, it establishes a new 'thought' folder for the user request, holding user input
        files and application created solution files
        The user prompt is added to a task queue, enabling the system to manage prompt resolution
        while allowing for early exit conditions if warranted.

        Parameters:
            user_prompt (str): The prompt provided by the user for processing.
        """
        if not self.is_prompt_valid(user_prompt):
            return  # Exit early on invalid input

        current_prompt_folder = os.path.join(FileManagement.thoughts_directory, f"{Globals.current_thought_id}")
        os.makedirs(current_prompt_folder, exist_ok=True)

        task_queue = deque([user_prompt])  # Main task queue
        Globals.workers = []

        while task_queue:
            task_to_execute_prompt = task_queue.popleft()  # Retrieve the next task
            self.handle_task_iterations(task_to_execute_prompt)

    def handle_task_iterations(self, task_to_execute_prompt: str):
        """
        Oversee the iterative processing of the task prompt until resolution is achieved or
        the maximum number of attempts is reached.

        Parameters:
            task_to_execute_prompt (str): The task prompt currently being processed.
        """
        attempt_count = 0  # Reset attempt counter for the current task
        Globals.current_request_cost = 0.0

        while self.within_budget() and attempt_count < self.MAX_TRIES:
            self._process_task_iteration(task_to_execute_prompt, attempt_count)
            attempt_count += 1

        if not self.within_budget() or attempt_count >= self.MAX_TRIES:
            self._log_and_save_unsolved_problem()

    def _process_task_iteration(self, current_user_prompt: str, attempt_count: int):
        """
        Execute a single iteration of task processing for the given user prompt

        Parameters:
            current_user_prompt (str): The prompt being processed.
            attempt_count (int): The current attempt number for processing.
        """
        ExecutionLogs.add_to_logs(f"Starting iteration: {attempt_count}")

        worker = Globals.workers.pop() if Globals.workers else None
        prompt_to_process = worker[PersonaConstants.INSTRUCTIONS] if worker else current_user_prompt

        try:
            persona = worker[PersonaConstants.TYPE] if worker else PersonaConstants.ANALYST
            self.persona_system.run_iteration(prompt_to_process, persona)

            if Globals.is_solved:
                self._log_request_completion(current_user_prompt, attempt_count)
                return
        except Exception as e:
            logging.exception(
                f"""Retry {attempt_count + 1}/{self.MAX_TRIES} failed for iteration {attempt_count} with prompt: 
                '{current_user_prompt}'""")
            ExecutionLogs.add_to_logs(f"Iteration {attempt_count} failed due to: {str(e)}.")

    @staticmethod
    def is_prompt_valid(user_prompt: str) -> bool:
        """Validate the user's input prompt against content and length restrictions.  # ToDo eventually...

        This method checks if the user prompt is appropriate for processing.

        Parameters:
            user_prompt (str): The prompt to be validated.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not isinstance(user_prompt, str):
            logging.error("Invalid input: user_prompt must be a non-empty string.")
            return False

        return True

    def _log_and_save_unsolved_problem(self):
        """Log and save information about an unsolved problem."""

        logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.MAX_TRIES} ATTEMPTS")
        ExecutionLogs.add_to_logs(f"PROBLEM REMAINS UNSOLVED AFTER {self.MAX_TRIES} ATTEMPTS\n")

    @staticmethod
    def _log_request_completion(task_to_execute: str, attempt_count: int):
        """Log the termination of a request process.

        Parameters:
            current_user_prompt (str): The prompt that was processed.
            attempt_count (int): Number of attempts made to fulfill the request.
        """
        logging.info(f"""FINISHED REQUEST: [{task_to_execute}]
                        Completed in {attempt_count} iterations
                        Total cost incurred: ${round(Globals.current_request_cost, 4)}""")

    @staticmethod
    def within_budget(budget: float = BUDGET) -> bool:
        """
        Evaluate whether the current request cost aligns with predefined budgetary constraints.

        This method compares the total costs incurred with the specified budget, returning
        True if expenses remain within limits, thereby preventing overspending on API calls.

        Parameters:
            budget (float): The budget cap for assessment. Default is the class-level BUDGET.

        Returns:
            bool: True if costs are within budget, False otherwise.
        """
        logging.info(
            f"""Current cost: ${round(Globals.current_request_cost, 5)}, 
            {round((Globals.current_request_cost / budget) * 100, 5)}%""")
        return Globals.current_request_cost <= budget


if __name__ == '__main__':
    thought_process = UserInterface()

    thought_process.process_user_prompt(
        """Make improvements to the available python file_name TaskType.py, focusing on improving logic and method flow, on clever solutions and to a much lesser degree readability. Consider changing variable names. Do not append to the document only rewrite bits of it"""
    )