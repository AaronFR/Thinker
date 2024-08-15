import enum
import json
import logging
from typing import List, Dict

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion

import Constants
import Globals
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from Utility import Utility


class ChatGptRole(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Prompter:

    def __init__(self):
        ErrorHandler.setup_logging()

        self.open_ai_client = OpenAI()

    @staticmethod
    def get_open_ai_function_response(messages: List[dict], function_schema, model=Constants.MODEL_NAME) -> Dict[str, object]:
        """Requests a structured response from the OpenAI API for function calling.

        :param messages: The system and user messages to send to the ChatGpt client
        :param function_schema:  The schema to apply to the output json
        :param model: the actual llm to call
        :return: The content of the response from OpenAI or an error message to inform the next executor task
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")
            chat_completion = Globals.open_ai_client.chat.completions.create(
                model=model,
                messages=messages,
                functions=function_schema,
                function_call={"name": "executiveDirective"}
                # ToDo investigate more roles
            )
            Prompter.calculate_prompt_cost(chat_completion, model)

            logging.info(f"Executive Plan: {chat_completion}")
            function_call = chat_completion.choices[0].message.function_call
            arguments = function_call.arguments
            json_object = json.loads(arguments)
            return json_object or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except OpenAIError:
            logging.error(f"OpenAI API error:")
            raise
        except Exception:
            logging.error(f"Unexpected error")
            raise

    def get_open_ai_response(self, messages: List[dict], model=Constants.MODEL_NAME) -> str | None:
        """Request a response from the OpenAI API.

        :param messages: The system and user messages to send to the ChatGpt client
        :param model: the actual llm being called
        :return: The content of the response from OpenAI or an error message to inform the next Executor.
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")
            chat_completion = self.open_ai_client.chat.completions.create(
                model=model, messages=messages
            )
            Prompter.calculate_prompt_cost(chat_completion, model)

            response = chat_completion.choices[0].message.content
            return response or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise


    @staticmethod
    def generate_messages(input_files, system_prompts: List[str] | str, user_prompts: List[str]) -> List[Dict[str, str]]:
        logging.debug(f"Thinking...{pformat(user_prompts, width=180)}")
        system_prompts = Utility.ensure_string_list(system_prompts)
        user_prompts = Utility.ensure_string_list(user_prompts)

        messages = Prompter.generate_role_messages(system_prompts, input_files, user_prompts)

        logging.debug(f"Messages: {pformat(messages)}")
        logging.info(f"Tokens used (limit 128k): {Utility.calculate_tokens_used(messages)}")

        #ToDo should be a warning message if messages exceed 100: probably means a string has been decomposed
        return messages

    @staticmethod
    def generate_role_messages(system_prompts: List[str], input_files: List[str], user_prompts: List[str]) -> List[Dict[str, str]]:
        """
        :param system_prompts: list of instructions to be saved as system info
        :param input_files: input file content for reference: taking the form of previous user input
        :param user_prompts: primary initial instruction and other supplied material
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

        role_messages = role_messages + [(Role.USER, prompt) for prompt in user_prompts]
        system_role_messages = [(Role.SYSTEM, prompt) for prompt in system_prompts]

        return Prompter.create_messages_by_role(role_messages + system_role_messages)

    @staticmethod
    def create_messages_by_role(role_messages: List[tuple]) -> List[Dict[str, str]]:
        """Create messages from a list of tuples containing role and content.

        :param role_messages: A list of tuples with each tuple containing a Role and its message content.
        :return: A list of dictionaries representing user messages.
        """
        messages = []
        for role, content in role_messages:
            messages.append({"role": role.value, "content": content})
        return messages

    @staticmethod
    def calculate_prompt_cost(chat_completion: ChatCompletion, model):
        """
        Currently assumes your using ChatGpt-4o mini

        :param chat_completion: after the prompt has been processed
        """

        if model == Constants.MODEL_NAME:
            input_token_price = chat_completion.usage.prompt_tokens * Constants.cost_per_input_token_gpt4o_mini
            output_token_price = chat_completion.usage.completion_tokens * Constants.cost_per_output_token_gpt4o_mini
        if model == Constants.EXPENSIVE_MODEL_NAME:
            logging.warning("EXPENSIVE MODEL USED!")
            input_token_price = chat_completion.usage.prompt_tokens * Constants.cost_per_input_token_gpt4o_mini
            output_token_price = chat_completion.usage.completion_tokens * Constants.cost_per_output_token_gpt4o_mini

        Globals.current_request_cost += (input_token_price + output_token_price)

        logging.info(
            f"""Input tokens: {chat_completion.usage.prompt_tokens}, price: ${round(input_token_price, 4)}
            Output tokens: {chat_completion.usage.completion_tokens}, price: ${round(output_token_price, 4)}
            Total cost: ¢{round((input_token_price + output_token_price) * 100, 4)}
        """)


if __name__ == '__main__':
    # Should probably read from an actual log file.
    prompter = Prompter()
    # prompts = ["Review [Prompter.py], try and re-write it solving any to-do's you spot",
    #            "Review [HtmlProcessing.py], try and re-write it solving any to-do's you spot"]

    prompter.process_prompt(
        "I want you to write a lengthy, detailed and well thought out report about the psychology of anger",  #"""Can you review the file I'll copy in below and give me any recomendations for improving logging? Specifically Logging Enhancements [README.md]""",
        1
    )
