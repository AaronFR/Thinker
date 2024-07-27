import logging
from typing import List
from openai import OpenAI
import Constants
import Prompter
from ThoughtProcessor.FileManagement import FileManagement
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
        user_messages = [{"role": "user", "content": prompt}] + [
            {"role": "user", "content": FileManagement.read_file(file)} for file in self.input_files
        ]
        return user_messages

    def get_openai_response(self, messages: List[dict]) -> str:
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
