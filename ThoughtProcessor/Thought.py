import logging
import os
from typing import List

from openai import OpenAI

import Constants
import Prompter
from Utility import Utility


class Thought:

    def __init__(self, input_files, prompter: Prompter.Prompter, open_ai_client: OpenAI):
        self.prompter = prompter
        self.open_ai_client = open_ai_client
        self.input_files = input_files

    def think(self, system_prompt: str, user_prompt: str) -> str:
        logging.info(f"Thinking...{user_prompt}")
        user_messages = self.create_user_messages(user_prompt)
        messages = [{"role": "system", "content": system_prompt}] + user_messages

        logging.debug(f"Messages: {messages}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        response = self.get_openai_response(messages)
        if not response:
            logging.error("No response from OpenAI API.")
            return "FATAL ERROR: NO RESPONSE FROM OPEN AI API, CONSIDER PROCESS TERMINATION"

        logging.info(f"Thought finished")
        return response

    def create_user_messages(self, prompt: str) -> List[dict]:
        file_contents = self.load_files(self.input_files)
        user_messages = [{"role": "user", "content": prompt}] + \
                        [{"role": "user", "content": content} for content in file_contents]
        return user_messages

    @staticmethod
    def load_file_content(file_path: str) -> str:
        full_path = os.path.join("Thoughts", "1", file_path)
        logging.info(f"Loading file content from: {full_path}")
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return f"[FAILED TO LOAD {file_path}]"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return f"[FAILED TO LOAD {file_path}]"

    def load_files(self, file_paths: List[str]) -> List[str]:
        contents = []
        for path in file_paths:
            logging.info(f"Attempting to access {path}")
            contents.append(self.load_file_content(path))
        return contents

    def get_openai_response(self, messages: List[dict]) -> str:
        model = Constants.MODEL_NAME
        try:
            response = self.open_ai_client.chat.completions.create(
                model=Constants.MODEL_NAME, messages=messages).choices[0].message.content
            return response or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except Exception as e:
            logging.error(f"Failed to get response from OpenAI: {e}")
            return "[ERROR: Failed to get response from OpenAI]"


if __name__ == '__main__':
    prompter = Prompter.Prompter()
    openai = OpenAI()
    thought = Thought(["Thought.py"], prompter, openai)

    print(thought.think(
        """Evaluate the following prompt to the best of your abilities adding as much useful detail as possible while 
        keeping your answer curt and to the point""",
        "How can the Thought.py be improved? Write an improved version"))
    # print(thought.think("Provide a detailed answer about Hideki Naganuma's background, contributions, and any relevant achievements."))
