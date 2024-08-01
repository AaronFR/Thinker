import json
import logging
from pprint import pformat
from typing import List, Dict
from openai import OpenAI, OpenAIError
import Constants
from Prompter import Prompter
from Utility import Utility





class Thought:
    """This class manages a single interaction with a llm. Each instance of 'Thought' is focused on
        understanding user input and generating an appropriate output based on that input."""


    def __init__(self, input_files: List[str], prompter: Prompter, open_ai_client: OpenAI):
        """Initializes a Thought instance that handles the interaction with the OpenAI API.

        :param input_files: A list of file names that users provide for analysis or reference in generating responses.
        :param prompter: An instance of the Prompter class, responsible for creating the prompts sent to the OpenAI API.
        :param open_ai_client: The OpenAI API client instance.
        """
        self.prompter = prompter
        self.open_ai_client = open_ai_client
        self.input_files = input_files

    def think(self, system_prompts: List[str] | str, user_prompt: str) -> str:
        """Generate a response based on system and user prompts.

        This method constructs messages to be sent to the OpenAI API and retrieves a response.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
        ToDo: With large context lengths approx 5k+ the current executive prompt can fail to produce an actual json output and get confused into writing a unironic answer
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompt: The task the thought process is to be dedicated to.
        :return: The response generated by OpenAI or an error message.
        """
        messages = self.generate_messages(system_prompts, user_prompt)

        response = Utility.execute_with_retries(lambda: self.get_open_ai_response(messages))
        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Executor Thought finished")
        return response

    def executive_think(self, system_prompts: List[str] | str, user_prompt: str) -> Dict[str, object]:
        """Generates a structured response based on system and user prompts for executive directives.
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'
        #Solved if executive files only review summaries of input files

        :param system_prompts: The system prompts to guide the thinking process.
        :param user_prompt: The specific task to address.
        :return: The response generated by OpenAI or an error message.
        """
        messages = self.generate_messages(system_prompts, user_prompt)

        response = Utility.execute_with_retries(lambda: self.get_open_ai_function_response(messages))
        if not response:
            logging.error("No response from OpenAI API.")
            raise Exception("Failed to get response from OpenAI API.")

        logging.info(f"Executive thought finished")
        return response

    def generate_messages(self, system_prompts: List[str] | str, user_prompt: str):
        logging.info(f"Thinking...{user_prompt}")
        if isinstance(system_prompts, str):
            system_prompts = [system_prompts]
        if not isinstance(system_prompts, list) or not all(isinstance(sp, str) for sp in system_prompts):
            raise ValueError("""system_prompts must be provided in the format of a list, where each element is a string. 
                    Please ensure compliance with this expected structure for proper functionality.""")

        messages = Prompter.generate_role_messages(system_prompts, self.input_files, user_prompt)

        logging.debug(f"Messages: {pformat(messages)}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        return messages

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

    def get_open_ai_function_response(self, messages: List[dict]) -> Dict[str, object]:
        """Requests a structured response from the OpenAI API for function calling.

        :param messages: The system and user messages to send to the ChatGpt client
        :return: The content of the response from OpenAI or an error message to inform the next Thought.
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")
            output = self.open_ai_client.chat.completions.create(
                model=Constants.MODEL_NAME,
                messages=messages,
                functions=Constants.EXECUTIVE_FUNCTIONS_SCHEME,
                function_call={"name": "executiveDirective"}
                # ToDo investigate more roles
            )
            logging.info(f"Executive Thought: {output}")
            function_call = output.choices[0].message.function_call
            arguments = function_call.arguments
            json_object = json.loads(arguments)
            return json_object or "[ERROR: NO RESPONSE FROM OpenAI API]"
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
        rewrite solution.txt to be more concise"""))
        #"How can the Thought.py be improved? Write an improved version"))
