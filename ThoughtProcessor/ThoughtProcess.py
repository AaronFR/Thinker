import json
import logging
import os
import re
from collections import deque
from pprint import pformat
from typing import List, Dict, Tuple

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
        """
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "Thoughts")
        self.files_to_evaluate = []
        self.thought_id = 1  # self.get_next_thought_id()
        FileManagement.initialise_file(self.thought_id, "solution.txt")  # ToDo: In future this might not be necessary

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
        ToDo: Should probably switch to using a DAG with edges

        :param task_description: The description of the task to evaluate as a string.
        """
        new_folder = os.path.join(self.thoughts_folder, f"{self.thought_id}")
        os.makedirs(new_folder, exist_ok=True)

        logs = ""
        task_queue = deque([task_description])  # Main task queue
        failed_tasks_queue = []  # Queue for failed tasks

        while task_queue:
            current_task = task_queue.popleft()  # Get the next task
            attempt_count = 0  # Reset attempt counter for the current task

            while attempt_count < self.max_tries:
                attempt_count += 1
                logging.info(f"Attempt {attempt_count} for task: {current_task}")
                self.files_to_evaluate = FileManagement.list_files(new_folder)

                try:
                    executive_output_dict = self.process_executive_thought(current_task)
                    logs += "EXEC PLAN: " + str(pformat(executive_output_dict)) + "\n"

                    if executive_output_dict.get('solved'):
                        logging.info(f"Task `{current_task}` solved successfully in attempt {attempt_count}.")
                        self.finalise_solution(self.thought_id, logs)
                        return  # Exit if the solution is found

                    logging.info(f"Generated tasks: {pformat(executive_output_dict.get('tasks'))}")
                    tasks = executive_output_dict.get('tasks', [])

                    for task in tasks:
                        try:
                            logging.info(f"Executing task: \n{pformat(task)}")
                            success, output = self.process_task(
                                task
                            )
                            if success:
                                logging.info(f"Task executed successfully: {task.get('what_to_do')}")
                            else:
                                failed_task = task.get('what_to_do')
                                logging.error(f"Task failed: {failed_task}. Output: {output}")
                                # failed_tasks_queue.append(failed_task)  # ToDo implement, for starters it needs
                                logs += f"Task failed: {failed_task} - Output: \n{output}"
                        except Exception as e:
                            logging.error(f"Error executing task `{task.get('what_to_do')}`: {e}")
                            failed_tasks_queue.append(task)  # Queue the failed task

                    if attempt_count == self.max_tries:
                        logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
                        logs += f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS\n"  # Capture final attempt logs
                        break

                except Exception as e:
                    logging.error(f"Error processing executive thought for `{current_task}`: {e}")
                    break  # Exit loop on processing executive thought failure

            # Process failed tasks if there are any
            if failed_tasks_queue:
                logging.info(f"Re-attempting failed tasks:... \n{pformat(failed_tasks_queue)}")
                for failed_task in failed_tasks_queue:
                    task_queue.append(failed_task)  # Add failed task back to the main task queue
                failed_tasks_queue.clear()  # Clear the failed tasks queue for the next set of executions

    def process_executive_thought(self, task: str) -> Dict[str, str]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :return: A dictionary parsed from the llm's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        executive_thought = self.create_next_thought(self.files_to_evaluate)
        executive_output = executive_thought.think([Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS], task)
        try:
            logging.info(f"Converting executive output from json format to dict: \n{executive_output}")
            # Remove the ```json and ``` at the start and end
            cleaned_json_string = re.sub(r'^```json\s*|\s*```$', '', executive_output.strip())
            return json.loads(cleaned_json_string)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON output: %s", executive_output)
            raise

    def process_thought(
            self,
            executive_directive: str,
            external_files: List[str],
            save_to: str,
            overwrite: bool = False
        ) -> Tuple[bool, str]:
        """
        Process the thoughts generated from the executive output and save results.

        ToDo: Should probably change system_message if its the first iteration

        :param executive_directive: Primary instruction for this task
        :param external_files: List of external files used as context.
        :param save_to: File path where output should be saved.
        :param overwrite: Boolean flag to determine if the output file should be overwritten. ToDo: Not currently in service
        :return: Tuple indicating success status and the output result.
        """
        try:
            logging.info("Processing Thought: " + executive_directive)
            thought = self.create_next_thought(external_files)
            output = thought.think(
                "Primary Instructions: " + str(executive_directive)
            )

            FileManagement.save_file(output, save_to, str(self.thought_id), overwrite)
                    Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            logging.info(f"Thought processed and saved to {save_to}.")
            return True, output  # Task was successful
        except Exception as e:
            logging.error(f"Output was empty or invalid: {e}")
            return False, ''  # Task failed

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
        """rewrite the README in a way that you think makes sense"""
    )
    #
    # # Please don't overwrite ThoughtProcess to fill it with theory, it needs to remain a valid python file as it was"""
    # # """Take ThoughtProcess.py and re-write so that method has a docstring. Please don't overwrite ThoughtProcess to fill it with theory, it needs to remain a valid python file as it was"""  # found to overwrite python files in a meaningful way
