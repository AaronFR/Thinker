import enum
import logging
from typing import List, Dict

from openai import OpenAI
from openai.types.chat import ChatCompletion

import Constants
from FileProcessing import FileProcessing
from ThoughtProcessor.FileManagement import FileManagement
from Utility import Utility


class Role(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


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

    @staticmethod
    def generate_role_messages(system_prompts: List[str], input_files: List[str], user_prompt: str):
        """
        ToDo: generalise for user_prompt***S***
        :param system_prompts: list of instructions to be saved as system info
        :param input_files: input file content for reference: taking the form of previous user input
        :param user_prompt: primary initial instruction
        :return:
        """
        role_messages = []

        # Add input file contents as user messages
        for file in input_files:
            try:
                content = FileManagement.read_file(file)
                role_messages.append((Role.USER, f"{file}: \n{content}"))
            except FileNotFoundError:
                logging.error(f"File not found: {file}. Please ensure the file exists.")
                role_messages.append((Role.USER, f"File not found: {file}"))
            except Exception as e:
                logging.error(f"Error reading file {file}: {e}")
                role_messages.append((Role.USER, f"Error reading file {file}. Exception: {e}"))

        # Add the user prompt
        role_messages.append((Role.USER, user_prompt))

        # Prepare system messages as role tuples
        system_role_messages = [(Role.SYSTEM, prompt) for prompt in system_prompts]

        return Prompter.create_messages_by_role(role_messages + system_role_messages)

    @staticmethod
    def generate_message(role: Role, content: str) -> Dict[str, str]:
        """Generate a message based on the specified role.

        :param role: The role of the message sender.
        :param content: The content of the message to be sent.
        :return: A dictionary representing the message.
        """
        return {"role": role.value, "content": content}

    @staticmethod
    def create_messages_by_role(role_messages: List[tuple]) -> List[Dict[str, str]]:
        """Create messages from a list of tuples containing role and content.

        :param role_messages: A list of tuples with each tuple containing a Role and its message content.
        :return: A list of dictionaries representing user messages.
        """
        messages = []
        for role, content in role_messages:
            messages.append(Prompter.generate_message(role, content))
        return messages


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
