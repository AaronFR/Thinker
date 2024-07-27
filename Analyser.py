import logging
from pprint import pprint
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
import time

from FileProcessing import FileProcessing


# Press Shift+F10 to execute it or replace it with your code.

class Analyser:
    def __init__(self):
        self.html_formatter = FileProcessing()
        self.MODEL_NAME = "gpt-4o-mini"

    def analyse_solution(self, initial_prompt: str, solution: str) -> ChatCompletionMessage | None:
        """
        To determine if the solution is satisfactory and cannot be improved.
        If it can be the flag will be set to false and ideally the solution should be re-run through again and again
        (to a limit) to try and improve the solution offered.

        :param initial_prompt: Initial 'big task' provided to the Sub Prompter
        :param solution: The derived and amalgamated solution from the multiple prompts of input
        :return: An analysis of the solution, crucially containing a 'Solved: True/False flag
        """
        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": """You are an analyst strictly reviewing the quality of a solution to a given problem, at the end of your through evaluation, determine if the given solution ACTUALLY answers the original prompt sufficiently in format:
                    Solved: True/False"""},
                    {"role": "user", "content": f"given the following initial prompt:{initial_prompt} how do you evaluate this solution?: {solution} \n\n\n Make as many notes and corrections as you possibly can"}


                ]
            )
            return response.choices[0].message
        except Exception as e:
            logging.error(f"Error during OpenAI API call: {e}")
            return None


if __name__ == '__main__':
    analyser = Analyser()
    analysis = analyser.analyse_solution("Comprehensive Python Example: Using Tuple, Dictionary, Module, Decorator, Generator, Polymorphism, and Asynchronous Programming", """bee""")

    html_processing = FileProcessing()
    pprint(analysis)
    html_processing.save_as_html(analysis.content, "Analysis", 1)
