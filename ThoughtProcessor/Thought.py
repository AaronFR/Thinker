import logging
from typing import List, Dict
from openai import OpenAI, OpenAIError
import Constants
from Prompter import Prompter
from Utility import Utility





class Thought:
    """This class manages a single interaction with a llm. Each instance of 'Thought' is focused on
        understanding user input and generating an appropriate output based on that input."""


    def __init__(self, input_files: List[str], prompter: Prompter, open_ai_client: OpenAI):
        """Each 'Thought' represents a single call to the api that then adds to the existing body of files representing
        a solution to the initial task that triggered the thought process.

        :param input_files: A list of file names that users provide for analysis or reference in generating responses.
        :param prompter: An instance of the Prompter class, responsible for creating the prompts sent to the OpenAI API.
        :param open_ai_client: The OpenAI API client instance.
        """
        self.prompter = prompter
        self.open_ai_client = open_ai_client
        self.input_files = input_files

    def think(self, system_prompts: List[str] | str, user_prompt: str) -> str:
        """Generate a response based on system and user prompts.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
        ToDo: With large context lengths approx 5k+ the current executive prompt can fail to produce an actual json output and get confused into writing a unironic answer
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompt: The task the thought process is to be dedicated to.
        :return: The response generated by OpenAI or an error message.
        """
        logging.info(f"Thinking...{user_prompt}")
        if isinstance(system_prompts, str):
            system_prompts = [system_prompts]
        if not isinstance(system_prompts, list) or not all(isinstance(sp, str) for sp in system_prompts):
            raise ValueError("system_prompts must be a list of strings.")

        messages = Prompter.generate_role_messages(system_prompts, self.input_files, user_prompt)

        logging.debug(f"Messages: {messages}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        response = Utility.execute_with_retries(lambda: self.get_open_ai_response(messages))
        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Thought finished")
        return response

    def get_open_ai_response(self, messages: List[dict]) -> str | None:
        """Request a response from the OpenAI API.

        :param messages: The system and user messages to send to the ChatGpt client
        :return: The content of the response from OpenAI or an error message to inform the next Thought.
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")
            response = self.open_ai_client.chat.completions.create(
                model=Constants.MODEL_NAME, messages=messages
            ).choices[0].message.content
            return response or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except OpenAIError:
            logging.error(f"OpenAI API error:")
            raise
        except Exception:
            logging.error(f"Unexpected error")
            raise


if __name__ == '__main__':
    prompter = Prompter()
    openai = OpenAI()
    thought = Thought(["solution.txt"], prompter, openai)

    print(thought.think(
        Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS,
        """
        Give me a history of India"""))
        #"How can the Thought.py be improved? Write an improved version"))
