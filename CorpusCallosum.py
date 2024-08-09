import asyncio
import json
import logging
import re
from pprint import pprint
from typing import Tuple, Dict
from openai.types.chat import ChatCompletionMessage

from Analyser import Analyser
from PromptManagement import PromptManagement
from FileProcessing import FileProcessing
from Prompter import Prompter
import Constants

with open('config.json', 'r') as file:
    config = json.load(file)
logging_level = getattr(logging, config['app']['logging']['level'])


class CorpusCallosum:
    """
    Orchestrates the generation and processing of tasks based on user prompts using OpenAI's API.

    This class is responsible for transforming initial prompts into structured action plans, categorizing tasks into
    parallel and sequential types, and managing their execution via various helper components.

    Attributes:
        prompter (Prompter): Handles prompt responses and interactions with OpenAI's API.
        prompt_management (PromptManagement): Manages the execution of parallel and sequential tasks.
        html_processing (FileProcessing): Handles formatting and saving of outputs in HTML format.
        analyser (Analyser): Analyzes responses and data as necessary for decision-making.
    """

    def __init__(self):
        self.prompter = Prompter()
        self.prompt_management = PromptManagement()
        self.html_processing = FileProcessing()
        self.analyser = Analyser()

    def plan_from_prompt(self, initial_prompt: str, expensive=False) -> ChatCompletionMessage:
        """
        Generates a plan of action based on the initial prompt, as a series of individual prompts

        EXPENSIVE MODE: Mini is x30 times cheaper than the base model, the cheap mode uses 5x calls to implement a more
        accurate plan than a single baseline model prompt

        :param initial_prompt: Initial 'big task' provided to the Sub Prompter
        :param expensive: determines if the expensive or affordable should be used
        :return: A structured ChatCompletionMessage containing the plan according to specified format or None if failed.
        """
        if expensive:
            print("OUCH!")

            return self.prompter.generate_response(
                f"given the following initial prompt:\n\n\n{initial_prompt}",
                Constants.PLAN_FROM_PROMPT_INSTRUCTIONS,
                Constants.EXPENSIVE_MODEL_NAME
            ).choices[0].message

        else:
            parallel_tasks = {k: v.format(initial_prompt=initial_prompt) for k, v in
                              Constants.parallel_planing_tasks.items()}
            sequential_tasks = {k: v.format(initial_prompt=initial_prompt) for k, v in
                                Constants.sequential_planing_tasks.items()}

            self.process_tasks(parallel_tasks, sequential_tasks)
            with open('output_html_files/Task_5.txt', 'r') as file:  # Will need to be updated if the planing tasks are updated
                plan_of_action = file.read()

            return self.prompter.generate_response(
                plan_of_action,
                Constants.EDIT_PLAN_OF_ACTION.format(initial_prompt=initial_prompt)
            ).choices[0].message

    @staticmethod
    def parse_plan(plan: str) -> Tuple[Dict[int, str], Dict[int, str]]:
        """
        Extracts parallel and sequential tasks from the provided task plan string.

        :param plan: The full plan string to be parsed.
        :return: A tuple of two dictionaries for parallel and sequential tasks.
        """
        parallel_tasks = {}
        sequential_tasks = {}

        try:
            parallel_section, sequential_section = plan.split("SEQUENTIAL TASKS:", 1) \
                if "SEQUENTIAL TASKS:" in plan else (plan, "")

            logging.info("PARALLEL SECTION:\n%s", parallel_section)
            logging.info("SEQUENTIAL SECTION:\n%s", sequential_section)  # why is debug level not displaying?

            parallel_matches = re.findall(Constants.ISOLATE_TASK_CONTENT_REGEX, parallel_section, flags=re.DOTALL)
            parallel_tasks = {int(task_number): task_content.strip() for task_number, task_content in parallel_matches}

            sequential_matches = re.findall(Constants.ISOLATE_TASK_CONTENT_REGEX, sequential_section, flags=re.DOTALL)
            sequential_tasks = {int(task_number): task_content.strip() for task_number, task_content in
                                sequential_matches}

        except ValueError:
            logging.exception(
                f"""Error parsing the tasks: 
                Parallel_tasks: {parallel_tasks}
                Sequential_tasks: {sequential_tasks}\n
                Ensure the format is correct.""")

        logging.info(f"Parallel Tasks: {parallel_tasks}")
        logging.info(f"Sequential Tasks: {sequential_tasks}")
        return parallel_tasks, sequential_tasks

    def process_tasks(self, parallel_tasks: Dict[int, str], sequential_tasks: Dict[int, str]):
        """
        Orchestrates the processing of tasks by executing parallel tasks first, followed by sequential tasks

        :param parallel_tasks: A dictionary of tasks to be processed in parallel.
        :param sequential_tasks: A dictionary of tasks to be processed sequentially.
        """
        if parallel_tasks:
            logging.info(f"Processing parallel tasks: {parallel_tasks}")
            self.prompt_management.process_parallel_prompts(parallel_tasks)
        if sequential_tasks:
            logging.info(f"Processing sequential tasks.{sequential_tasks}")
            self.prompt_management.process_sequential_prompts(sequential_tasks)

        number_of_tasks = len(parallel_tasks) + len(sequential_tasks)
        html_processing.aggregate_files("Task", 1, number_of_tasks)


if __name__ == '__main__':
    html_processing = FileProcessing()
    corpus_callosum = CorpusCallosum()

    plan = corpus_callosum.plan_from_prompt(
        """Write out a full, fascinating, interesting and detailed report on the full breadth of Indian History -op het Nederlands!"""
    ).content

    html_processing.save_as_html(plan, "CC_plan", 10)
    parallel_tasks, sequential_tasks = corpus_callosum.parse_plan(plan)
    corpus_callosum.process_tasks(parallel_tasks, sequential_tasks)

    pprint(plan)
