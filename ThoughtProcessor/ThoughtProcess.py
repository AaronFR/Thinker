import json
import logging
import os
from typing import List, Dict

from openai import OpenAI

import Constants
from FileProcessing import FileProcessing
from Prompter import Prompter
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Thought import Thought

file_to_evaluate = "Thought.py"
files_to_evaluate = [file_to_evaluate, "ThoughtProcess.py"]  # placeholder


class ThoughtProcess:
    """
    Class to handle the process of evaluating tasks using the Thought class.
    """

    def __init__(self):
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "Thoughts")
        self.thought_id = 1  # self.get_next_thought_id()
        self.prompter = Prompter()
        self.open_ai_client = OpenAI()
        self.max_tries = 2
        FileManagement.initialise_file(self.thought_id, "solution.txt")

    def get_next_thought_id(self) -> int:
        """Get the next available thought ID based on existing directories."""
        os.makedirs(self.thoughts_folder, exist_ok=True)
        return len([name for name in os.listdir(self.thoughts_folder) if
                    os.path.isdir(os.path.join(self.thoughts_folder, name))]) + 1

    def evaluate_task(self, task: str):
        """Evaluate the given task and attempt to provide an optimised solution.

        Should probably switch to using a DAG with edges"""
        new_folder = os.path.join(self.thoughts_folder, f"{self.thought_id}")
        os.makedirs(new_folder, exist_ok=True)

        first_thought = self.create_next_thought(files_to_evaluate)
        initial_response = first_thought.think("""Evaluate the following  prompt thoroughly but concisely. Adding as much useful detail as possible while 
        keeping your answer curt and to the point.""", task)
        FileManagement.save_to_solution(initial_response, str(self.thought_id))

        logs = ""
        for iteration in range(1, self.max_tries + 1):
            external_files = [file_to_evaluate, "solution.txt"]  # hard coded for now
            logging.info(f"Starting iteration {iteration} for task: {task}")

            executive_output_dict = self.process_executive_thought("")
            logs += str(executive_output_dict)
            print(f"executive output: {executive_output_dict.get('next_steps')}")
            if executive_output_dict.get('solved'):
                self.finalise_solution(iteration, logs)
                break

            self.process_thought(executive_output_dict, external_files)
        else:
            logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
            print("Logs: ", logs)

    def process_executive_thought(self, task: str) -> Dict[str, str]:
        executive_thought = self.create_next_thought([file_to_evaluate, "solution.txt"])
        executive_output = executive_thought.think(Constants.EXECUTIVE_PROMPT, task)
        try:
            logging.info(f"Converting executive output from json format to dict: \n{executive_output}")
            return json.loads(executive_output)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON output: %s", executive_output)
            raise

    def process_thought(self, executive_output_dict: Dict[str, str], external_files: List[str]):
        thought = self.create_next_thought(external_files)
        output = thought.think(
            Constants.PROMPT_FOLLOWING_EXECUTIVE_DIRECTION,
            str(executive_output_dict.get('next_steps')) + "/n" + str(
                executive_output_dict.get('areas_of_improvement')))
        FileManagement.save_to_solution(output, str(self.thought_id))

    def create_next_thought(self, input_data) -> Thought:
        # Central management of thought instances
        new_thought = Thought(input_data, self.prompter, self.open_ai_client)
        return new_thought

    def finalise_solution(self, iteration: int, logs: str) -> None:
        print(f"Solved by iteration: {iteration}")
        FileProcessing.save_as_text(logs, os.path.join(self.thoughts_folder, str(iteration), "logs"), "")


if __name__ == '__main__':
    thought_process = ThoughtProcess()
    thought_process.evaluate_task(f"""Make a series of small improvements to  {file_to_evaluate} and ThoughtProcess.py, focus on logic improvements, flow changes and improved readability/understandability""")
