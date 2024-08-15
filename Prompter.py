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
