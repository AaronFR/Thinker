import json
import logging
import os
from typing import List, Dict

from openai import OpenAI

import Constants
from Prompter import Prompter
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Thought import Thought


class ThoughtProcess:
    """
    Class to handle the process of evaluating tasks using the Thought class.
    """

    def __init__(self, files_to_evaluate):
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "Thoughts")
        self.files_to_evaluate = files_to_evaluate
        self.thought_id = 1  # self.get_next_thought_id()
        FileManagement.initialise_file(self.thought_id, "solution.txt")

        self.prompter = Prompter()
        self.open_ai_client = OpenAI()
        self.max_tries = 2

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

        logs = ""
        for iteration in range(1, self.max_tries + 1):
            logging.info(f"Starting iteration {iteration} for task: {task}")

            executive_output_dict = self.process_executive_thought(task)
            logs += str(executive_output_dict)
            print(f"executive output: {executive_output_dict.get('next_steps')}")
            if executive_output_dict.get('solved'):
                self.finalise_solution(self.thought_id, logs)
                break

            self.process_thought(executive_output_dict, self.files_to_evaluate)
        else:
            logging.error(f"PROBLEM REMAINS UNSOLVED AFTER {self.max_tries} ATTEMPTS")
            FileManagement.save_file(logs, os.path.join(self.thoughts_folder, str(self.thought_id), "logs.txt"), "")

    def process_executive_thought(self, task: str) -> Dict[str, str]:
        executive_thought = self.create_next_thought(self.files_to_evaluate)
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
        FileManagement.save_file(logs, os.path.join(self.thoughts_folder, str(iteration), "logs.txt"), "")


if __name__ == '__main__':
    thought_process = ThoughtProcess(["ThoughtProcess.py", "solution.txt"])
    thought_process.evaluate_task(
        f"""Write up a refactoring for "ThoughtProcess.py": In the current flow an initial Thought is created that then 
        writes to solution.txt, then a loop is started which goes thought -> new executive, where the prior executive 
        thought tells the next thought in the loop what to do, in reality there should be no initial thought, 
        just going straight into the processing loop, where an executive thought is triggered that tells a new thought 
        what to do in the same iteration of the loop"""
    )
