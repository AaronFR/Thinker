import asyncio
import concurrent.futures
import json
import logging
from asyncio import as_completed
from ThoughtProcessor import FileManagement
from typing import List, Dict

from Prompter import Prompter


class PromptManagement:

    def __init__(self):
        self.html_formatter = FileManagement
        self.prompter = Prompter()

    def send_prompt_list(self, prompts: List[str]):
        """Processes a list of prompts sequentially."""
        if not prompts:
            logging.warning("Received an empty prompt list.")
            return

        for promptId, prompt in enumerate(prompts, start=1):
            logging.debug(f"Processing prompt {promptId}: {prompt}")
            self.prompter.process_prompt(prompt, promptId)

    def process_parallel_prompts(self, parallel_tasks: Dict[int, str]):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.prompter.process_prompt, task, task_number): task_number
                for task_number, task in parallel_tasks.items()
            }

            for future in concurrent.futures.as_completed(futures):
                task_number = futures[future]
                try:
                    result = future.result()
                    logging.info(f"Task {task_number} completed with result: {result}")
                except Exception as exc:
                    logging.error(f'Task {task_number} raised an exception: {exc}')

    def process_sequential_prompts(self, sequential_tasks: Dict[int, str]):
        """
        Processes tasks sequentially and handles a special 'publish' flag on the last task.
        ToDo the final if statement should instead check for a [Output] tag allowing for multiple output files, but the entire system has to be changed to accomoddate that

        :param sequential_tasks: list of final, sequential tasks for completing a given task
        """
        if not sequential_tasks:
            logging.warning("Received an empty dictionary of sequential tasks.")
            return

        last_task_number = max(sequential_tasks.keys())

        for task_number, task in sequential_tasks.items():
            logging.debug(f"Processing task {task_number} out of {last_task_number}.")
            if task_number != last_task_number:
                self.prompter.process_prompt(task, task_number)
            else:
                self.prompter.process_prompt(task, task_number, True)
