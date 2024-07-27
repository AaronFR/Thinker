import json
import logging
import os
from typing import List, Dict

from openai import OpenAI

import Constants
from FileProcessing import FileProcessing
from Prompter import Prompter
from ThoughtProcessor.Thought import Thought

file_to_evaluate = "ThoughtProcess.py"  # placeholder

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
        self.initialise_file(self.thought_id, "solution.txt")

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

        first_thought = self.create_next_thought([file_to_evaluate])
        first_attempt = first_thought.think("""Evaluate the following  prompt thoroughly but concisely. Adding as much useful detail as possible while 
        keeping your answer curt and to the point.""", task)
        self.save_to_solution(first_attempt, str(self.thought_id))

        logs = ""
        for iteration in range(1, self.max_tries + 1):
            external_files = [file_to_evaluate, "solution.txt"]  # hard coded for now
            logging.info(f"Starting iteration {iteration} for task: {task}")

            executive_output_dict = self.process_executive_thought("")
            logs += str(executive_output_dict)
            print(f"executive output: {executive_output_dict.get('next_steps')}")
            if executive_output_dict.get('solved'):
                self.finalize_solution(iteration, logs)
                break

            self.process_thought(executive_output_dict, external_files)
        else:
            logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
            print("Logs: ", logs)

    def process_executive_thought(self, task: str) -> Dict[str, str]:
        executive_thought = self.create_next_thought([file_to_evaluate, "solution.txt"])
        executive_output = executive_thought.think(Constants.EXECUTIVE_PROMPT, task)
        try:
            return json.loads(executive_output)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from executive output.")
            raise

    def process_thought(self, executive_output_dict: Dict[str, str], external_files: List[str]):
        thought = self.create_next_thought(external_files)
        output = thought.think(
            Constants.PROMPT_FOLLOWING_EXECUTIVE_DIRECTION,
            str(executive_output_dict.get('next_steps')) + "/n" + str(
                executive_output_dict.get('areas_of_improvement')))
        ThoughtProcess.save_to_solution(output, str(self.thought_id))

    def create_next_thought(self, input_data) -> Thought:
        # Central management of thought instances
        new_thought = Thought(input_data, self.prompter, self.open_ai_client)
        return new_thought

    def finalize_solution(self, iteration: int, logs: str) -> None:
        print(f"Solved by iteration: {iteration}")
        FileProcessing.save_as_text(logs, os.path.join(self.thoughts_folder, "logs"), "")

    @staticmethod
    def initialise_file(thought_id: int, file: str):
        """Initialise the solution.txt file"""
        os.makedirs(f"Thoughts/{thought_id}", exist_ok=True)
        file_path = os.path.join("Thoughts", str(thought_id), file)
        try:
            with open(file_path, "w", encoding="utf-8"):
                logging.info(f"File {file_path} instantiated.")
        except Exception as e:
            logging.error(f"ERROR: could not save instantiate file: {file_path}\n {str(e)} \nThought_id: {thought_id}")

    @staticmethod
    def save_to_solution(content: str, thought_id: str):
        """Append content to the solution.txt file for a given thought"""
        file_path = f"Thoughts/{thought_id}/solution.txt"
        try:
            logging.info(f"{thought_id}: Attempting to save solution")

            with open(file_path, "a", encoding="utf-8") as file:
                file.write(content + "\n")
                logging.info(f"Solution saved for thought_id: {thought_id}")
        except Exception as e:
            logging.error(f"ERROR: could not save file, {str(e)} \n Thought_id: {thought_id}")

    @staticmethod
    def read_solution(thought_id: str) -> str:
        """Read a given solution.txt file for a given thought id number"""

        file_path = f"Thoughts/{thought_id}/solution.txt"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logging.error(f"ERROR: could not save file, {str(e)}")
            return "[FATAL ERROR COULD NOT READ SOLUTION]"


if __name__ == '__main__':
    thought_process = ThoughtProcess()
    # thought_process.save_solution("Test", "1")
    # print(thought_process.read_solution("1"))
    thought_process.evaluate_task(f"""How would you improve {file_to_evaluate}? Write an improved version""")
