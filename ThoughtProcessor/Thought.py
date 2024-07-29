import logging
from typing import List
from openai import OpenAI
import Constants
import Prompter
from ThoughtProcessor.FileManagement import FileManagement
from Utility import Utility


class Thought:
    """Class to manage and process 'thoughts' in the Thinker system using the OpenAI API"""

    def __init__(self, input_files: List[str], prompter: Prompter.Prompter, open_ai_client: OpenAI):
        """Each 'Thought' represents a single call to the api that then adds to the existing body of files representing
        a solution to the initial task that triggered the thought process.

        :param input_files: file references representing files passed in by the user for processing/reference
        :param prompter: handles prompting the OpenAi API
        :param open_ai_client: The OpenAI API client instance.
        """
        self.prompter = prompter
        self.open_ai_client = open_ai_client
        self.input_files = input_files

    def think(self, system_prompts: List[str], user_prompt: str) -> str:
        """Generate a response based on system and user prompts.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
        ToDo: With large context lengths approx 5k+ the current executive prompt can fail to produce an actual json output and get confused into writing a unironic answer
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompt: The task the thought process is to be dedicated to.
        :return: The response generated by OpenAI or an error message.
        """
        logging.info(f"Thinking...{user_prompt}")
        user_messages = self.create_user_messages(user_prompt)
        system_messages = self.create_system_messages(system_prompts)
        messages = system_messages + user_messages

        logging.info(f"Messages: {messages}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        response = self.get_open_ai_response(messages)
        if not response:
            logging.error("No response from OpenAI API.")
            return "FATAL ERROR: NO RESPONSE FROM OPEN AI API, CONSIDER PROCESS TERMINATION"

        logging.info(f"Thought finished")
        return response

    def create_system_messages(self, prompts: List[str]) -> List[dict]:
        """Create user messages for a ChatGpt request. First consisting of the current content, lastly the task it is to
        'think' over.
        ToDo: eventually will need to be selective in the files it processes for very large requests

        :param prompts: List of system prompts to follow.
        :return: A list of dictionaries representing user messages.
        """
        if type(prompts) == str:  # otherwise it will split the single input into individual characters
            system_messages = [{"role": "system", "content": prompts}]
        else:
            system_messages = [
                {"role": "system", "content": prompt} for prompt in prompts
            ]
        logging.info(f"system_messages = \n{system_messages}")
        return system_messages

    def create_user_messages(self, prompt: str) -> List[dict]:
        """Create user messages for a ChatGpt request. First consisting of the current content, lastly the task it is to
        'think' over.
        ToDo: eventually will need to be selective in the files it processes for very large requests

        :param prompt: The user's prompt.
        :return: A list of dictionaries representing user messages.
        """
        user_messages = [
            {"role": "user", "content": file + ": \n" + FileManagement.read_file(file)} for file in self.input_files
        ] + [{"role": "user", "content": prompt}]
        logging.info(f"user_messages = \n{user_messages}")
        return user_messages

    def get_open_ai_response(self, messages: List[dict]) -> str:
        """Request a response from the OpenAI API.

        :param messages: The system and user messages to send to the ChatGpt client
        :return: The content of the response from OpenAI or an error message to inform the next Thought.
        """
        try:
            logging.info(f"Calling OpenAI API with messages: {messages}")
            response = self.open_ai_client.chat.completions.create(
                model=Constants.MODEL_NAME, messages=messages).choices[0].message.content
            return response or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except Exception as e:
            logging.error(f"Failed to get response from OpenAI: {e}")
            return "[ERROR: Failed to get response from OpenAI]"


if __name__ == '__main__':
    prompter = Prompter.Prompter()
    openai = OpenAI()
    thought = Thought(["solution.txt"], prompter, openai)

    print(thought.think(
        Constants.EXECUTIVE_PROMPT,
        """
        Give me a history of India"""))
        #"How can the Thought.py be improved? Write an improved version"))
