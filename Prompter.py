import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletion

import Constants
from FileProcessing import FileProcessing
from Utility import Utility


class Prompter:
    def __init__(self):
        self.html_formatter = FileProcessing()
        self.OPEN_AI_CLIENT = OpenAI()

    def process_prompt(self, prompt: str, task_number: int, publish_output=False):
        """
        Process a prompt to generate a response from the OpenAI API.

        :param prompt: The content of the task
        :param task_number: The tasks number in the execution sequence
        :param publish_output: if enabled as well as writing results as text, output will be saved in html format
        """
        prompt = Utility.fill_placeholders(prompt)

        try:
            output_text = self.generate_response(prompt).choices[0].message.content

            self.save_output(output_text, task_number, publish_output)
            logging.info(f"Task {task_number} processed successfully.")
        except Exception as e:
            logging.error(f"Error during OpenAI API call: {e}")

    def generate_response(self,
                          prompt: str,
                          system_prompt=Constants.EVALUATE_TASKS_INSTRUCTIONS,
                          model=Constants.MODEL_NAME) -> ChatCompletion:
        """Generate ChatCompletion response from OpenAI API for a given prompt."""
        logging.debug(f"Generating response for prompt: {prompt[:20]}...")
        return self.OPEN_AI_CLIENT.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(prompt)}
            ]
            # ToDo investigate more roles
        )

    def save_output(self, output_text: str, task_number: int, publish_output: bool) -> None:
        """Save the output text to a file."""
        self.html_formatter.save_as_text(output_text, "Task", task_number)
        if publish_output:
            logging.debug("Saving last Task as html")
            self.html_formatter.save_as_html(output_text, "Final_Task", task_number)


if __name__ == '__main__':
    # Should probably read from an actual log file.
    prompter = Prompter()
    html_processing = FileProcessing()
    # prompts = ["Review [Prompter.py], try and re-write it solving any ToDo's you spot",
    #            "Review [HtmlProcessing.py], try and re-write it solving any ToDo's you spot"]

    prompter.process_prompt(
        "I want you to write a lengthy, detailed and well thought out report about the psychology of anger",  #"""Can you review the file I'll copy in below and give me any recomendations for improving logging? Specifically Logging Enhancements [README.md]""",
        1
    )
