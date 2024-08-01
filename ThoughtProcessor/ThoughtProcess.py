import enum
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


class ThoughtType(enum.Enum):
    APPEND = "APPEND"
    REWRITE = "REWRITE"


class ThoughtProcess:
    """
    Class to handle the process of evaluating tasks using the Thought class.

    The ThoughtProcess orchestrates the flow of task evaluation by breaking user prompts down into actionable
    thoughts. The process includes multiple retries for task execution, allowing
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
        FileManagement.initialise_file(self.current_thought_id, "solution.txt")  # ToDo: In future this might not be necessary

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
        Evaluate and execute a task based on its description.

        This method coordinates the assessment and execution process, generating execution plans,
        attempting the resolution iteratively, and keeping logs of performance outcomes.

        :param task_description: The description of the task to evaluate as a string.
        """
        current_prompt_folder = os.path.join(self.thoughts_folder, f"{self.current_thought_id}")
        os.makedirs(current_prompt_folder, exist_ok=True)

        task_queue = deque([task_description])  # Main task queue
        failed_tasks_queue = []  # Queue for failed tasks

        while task_queue:
            execution_logs = ""
            current_task = task_queue.popleft()  # Get the next task
            attempt_count = 0  # Reset attempt counter for the current task

            # Iterate through execution attempts for a given task
            while attempt_count < self.max_tries:
                attempt_count += 1
                logging.info(f"Attempt {attempt_count} for task: {current_task}")
                self.files_for_evaluation = FileManagement.list_files(current_prompt_folder)

                try:
                    executive_output_dict = self.generate_executive_plan(current_task)
                    execution_logs += "EXEC PLAN: " + str(pformat(executive_output_dict)) + "\n"

                    if executive_output_dict.get('solved'):
                        logging.info(f"Task `{current_task}` solved successfully in attempt {attempt_count}.")

                        self.finalise_solution(self.current_thought_id, execution_logs)
                        return  # Exit if the solution is found

                    logging.info(f"Generated tasks: {pformat(executive_output_dict.get('tasks'))}")
                    tasks = executive_output_dict.get('tasks', [])

                    for task in tasks:
                        try:
                            logging.info(f"Executing task: \n{pformat(task)}")
                            success, output = self.execute_task(
                                task
                            )
                            if success:
                                logging.info(f"Task executed successfully: {task.get('what_to_do')}")
                            else:
                                failed_task = task.get('what_to_do')
                                logging.error(f"Task failed: {failed_task}. Output: {output}")
                                # failed_tasks_queue.append(failed_task)  # ToDo implement, for starters it needs
                                execution_logs += f"Task failed: {failed_task} - Output: \n{output}"
                        except Exception as e:
                            logging.error(f"Error executing task `{task.get('what_to_do')}`: {e}")
                            failed_tasks_queue.append(task)  # Queue the failed task

                    if attempt_count == self.max_tries:
                        logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
                        execution_logs += f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS\n"  # Capture final attempt logs
                        break

                except Exception as e:
                    logging.error(f"Error processing executive thought for `{current_task}`: {e}")
                    break  # Exit loop on processing executive thought failure

            FileManagement.save_file(
                execution_logs,
                os.path.join(self.thoughts_folder, str(self.current_thought_id), "execution_logs.txt"),
                ""
            )

            # Process failed tasks if there are any
            if failed_tasks_queue:
                logging.info(f"Re-attempting failed tasks:... \n{pformat(failed_tasks_queue)}")
                for failed_task in failed_tasks_queue:
                    task_queue.append(failed_task)  # Add failed task back to the main task queue
                failed_tasks_queue.clear()  # Clear the failed tasks queue for the next set of executions

    @staticmethod
    def re_write_section(text: str, replace: str, replacement: str) -> str:
        """
        Modify a specific section of the code based on an item identifier and replace it with new content.

        :param text: The original str text
        :param replace: The identifier for the section to be replaced (e.g., "Item 4").
        :param replacement: The replacement content as a string.
        :return: The modified code.
        """
        # Regex pattern to find the section based on the item identifier
        pattern = re.compile(
            r'(?P<target>' + re.escape(replace) + r'.*?)(?=\n\n|\Z)',
            re.DOTALL
        )

        # Replace the matched section with the replacement content
        modified_code = pattern.sub(replacement, text)

        return modified_code

    def generate_executive_plan(self, task: str) -> Dict[str, object]:
        """
        Process and obtain the new executive directive for the initial task.

        :param task: The initial task from the user.
        :return: A dictionary parsed from the llm's JSON format output.
        :raises JSONDecodeError: If the executive output cannot be parsed to a dictionary.
        """
        executive_thought = self.create_next_thought(self.files_for_evaluation)
        executive_output = executive_thought.executive_think([Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS], task)

        return executive_output

    def execute_task(
            self,
            task_directives: Dict[str, str],
            overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        Process the thoughts generated from the executive output and save results.

        This method carries out the task as dictated by the executive output, based on the instructions
        provided.
        ToDo: Should probably change system_message if its the first iteration

        :param task_directives: Dict with the executive thought's instructions for this task
        :return: Tuple indicating success status and the output result of executing the task.
        """
        thought_type = task_directives.get('type')
        primary_instruction = task_directives.get('what_to_do')
        external_files = task_directives.get('what_to_reference', [])
        save_to = task_directives.get('where_to_do_it')

        if not thought_type:
            thought_type = ThoughtType.APPEND.value

        try:
            logging.debug("Type input bug: = " + str(type(primary_instruction)))

            logging.info(f"Processing Thought: [{thought_type}]" + primary_instruction)
            executor_thought = self.create_next_thought(external_files)

            if thought_type == ThoughtType.APPEND.value:
                output = executor_thought.think(
                    Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
                    "Primary Instructions: " + str(primary_instruction)
                )
                FileManagement.save_file(output, save_to, str(self.current_thought_id), overwrite)
            if thought_type == ThoughtType.REWRITE.value:
                output = executor_thought.think(
                    Constants.REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS,
                    f"""Just rewrite <to_rewrite>\n{task_directives.get('what_to_rewrite')}\n</to_rewrite>\n
                    In the following way: {str(primary_instruction)}"""
                )
                FileManagement.re_write_section(task_directives.get('what_to_rewrite'), output, save_to,
                                                str(self.current_thought_id))
            # ToDO APPEND and REWRITE to a enum, then check message is present in enum

            logging.info(f"Thought processed and saved to {save_to}.")
            return True, output  # Task was successful
        except Exception as e:
            logging.error(f"Output was empty or invalid: {e}")
            return False, ''  # Task failed

    def rewrite_thought(self, thought: Thought, task_directives: Dict[str, str]):
        output = thought.think(
            Constants.EXECUTOR_SYSTEM_INSTRUCTIONS,
            f"""Just rewrite <to_rewrite>\n{task_directives.get('what_to_rewrite')}\n</to_rewrite>\n
            In the following way: {str(task_directives.get('what_to_do'))}"""
        )
        FileManagement.re_write_section(task_directives.get('what_to_rewrite'),
                                        output,
                                        task_directives.get('where_to_do_it'),
                                        str(self.current_thought_id))

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
        FileManagement.save_file(logs, os.path.join(self.thoughts_folder, str(self.current_thought_id), "logs.txt"), "")


if __name__ == '__main__':
    ErrorHandler.setup_logging()
    openai = OpenAI()
    prompter = Prompter()
    thought_process = ThoughtProcess()
    thought = Thought(["ThoughtProcess.py"], prompter, openai)

    thought_process.evaluate_and_execute_task(
        """Rewrite ThoughtProcess.py to be more intuitive and understandable at a glance, make your suggestions in 
        suggestions.md only, not editing the original python class"""
    )

    # thought_process.rewrite_thought(thought,
    # {
    #     'type': "REWRITE",
    #     'what_to_reference': ['Thought.py'],
    #     'what_to_rewrite': """\"\"\"Generate a response based on system and user prompts.
    #     ToDo: At some point actions other than writing will be needed, e.g. 'web search'
    #     ToDo: With large context lengths approx 5k+ the current executive prompt can fail to produce an actual json output and get confused into writing a unironic answer
    #     #Solved if executive files only review summaries of input files
    #
    #     :param system_prompts: The system prompts to guide the thinking process.
    #     :param user_prompt: The task the thought process is to be dedicated to.
    #     :return: The response generated by OpenAI or an error message.
    #     \"\"\"""",
    #     'what_to_do': "Rewrite this docstring in portugeuese, don't forget the triple commas, don't write anything ABOUT doing the task just do it, do not add a code block delimtiter, don't add a language identifier",
    #     'where_to_do_it': 'Thought.py'
    # }
    # )

    #
    # # Please don't overwrite ThoughtProcess to fill it with theory, it needs to remain a valid python file as it was"""
    # # """Take ThoughtProcess.py and re-write so that method has a docstring. Please don't overwrite ThoughtProcess to fill it with theory, it needs to remain a valid python file as it was"""  # found to overwrite python files in a meaningful way
