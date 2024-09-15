import enum
import json
import logging
import os
from typing import List, Dict

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion

from Utilities import Globals
from Utilities.ErrorHandler import ErrorHandler


class ChatGptModel(enum.Enum):
    """OpenAI API Models"""
    CHAT_GPT_4_OMNI_MINI = "gpt-4o-mini"
    CHAT_GPT_4_OMNI = "gpt-4o"


class ChatGptRole(enum.Enum):
    """Defines roles in the chat completion interaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class CostConfiguration:
    """Handles cost configuration for API calls."""

    def __init__(self):
        """Initialize cost settings from environment variables or defaults."""
        self.input_token_costs = {model: float(os.environ.get(f'INPUT_COST_{model.name}', default)) for model, default in {
            ChatGptModel.CHAT_GPT_4_OMNI_MINI: 0.00000015,  # $/t
            ChatGptModel.CHAT_GPT_4_OMNI: 0.000005,  # $/t
        }.items()}

        self.output_token_costs = {model: float(os.environ.get(f'OUTPUT_COST_{model.name}', default)) for model, default in {
            ChatGptModel.CHAT_GPT_4_OMNI_MINI: 0.00000060,  # $/t
            ChatGptModel.CHAT_GPT_4_OMNI: 0.000015,  # $/t
        }.items()}

class ChatGptWrapper:

    _instance = None

    def __new__(cls):
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(ChatGptWrapper, cls).__new__(cls)
            cls._instance.open_ai_client = OpenAI()  # Initialize the OpenAI client
            cls._instance.cost_config = CostConfiguration()  # Load cost configurations
        return cls._instance

    def get_open_ai_response(
            self,
            messages: List[Dict[str, str]],
            model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
            rerun_count=1) -> str | List[str]:
        """Request a response from the OpenAI API.

        :param messages: The system and user messages to send to the ChatGpt client
        :param model: the actual llm being called
        :param rerun_count: number of times to rerun the prompt
        :return: The content of the response from OpenAI or an error message to inform the next Executor
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")

            chat_completion = self.open_ai_client.chat.completions.create(
                model=model.value, messages=messages, n=rerun_count
            )
            self.calculate_prompt_cost(chat_completion, model)

            responses = [choice.message.content for choice in chat_completion.choices]
            return responses[0] if rerun_count == 1 else responses or None
        except OpenAIError as e:
            logging.exception(f"OpenAI API error", exc_info=e)
            raise
        except Exception as e:
            logging.exception(f"Unexpected error", exc_info=e)
            raise

    def get_open_ai_function_response(self,
                                      messages: List[Dict[str, str]],
                                      function_schema,
                                      model=ChatGptModel.CHAT_GPT_4_OMNI_MINI) -> Dict[str, object]:
        """Requests a structured response from the OpenAI API for function calling.

        :param messages: Messages sent to the ChatGPT client
        :param function_schema: Expected schema for the function output
        :param model: The specific language model to use.
        :return: The content of the response from OpenAI or an error message to inform the next executor task
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")
            chat_completion = self.open_ai_client.chat.completions.create(
                model=model.value,
                messages=messages,
                functions=function_schema,
                function_call={"name": "executiveDirective"}
                # ToDo:investigate more roles
            )
            self.calculate_prompt_cost(chat_completion, model)

            arguments = chat_completion.choices[0].message.function_call.arguments
            return json.loads(arguments) if arguments else {"error": "NO RESPONSE FROM OpenAI API"}
        except OpenAIError:
            logging.error(f"OpenAI API error:")
            raise
        except Exception:
            logging.error(f"Unexpected error")
            raise

    def calculate_prompt_cost(self, chat_completion: ChatCompletion, model: ChatGptModel):
        """Calculates the estimated cost of a call to OpenAi ChatGpt Api

        :param chat_completion: after the prompt has been processed
        :param model: the specific OpenAI model being used, the non Mini version is *very* expensive,
        and should be used rarely
        """
        input_tokens = chat_completion.usage.prompt_tokens
        output_tokens = chat_completion.usage.completion_tokens

        total_cost = (
            (input_tokens * self.cost_config.input_token_costs[model]) +
            (output_tokens * self.cost_config.output_token_costs[model])
        )
        Globals.current_request_cost += total_cost

        logging.info(
            f"Request cost - Input tokens: {input_tokens}, Output tokens: {output_tokens}, "
            f"Total cost: ${total_cost:.4f}"
        )


if __name__ == '__main__':
    ChatGptWrapper = ChatGptWrapper()

    output = ChatGptWrapper.get_open_ai_response([
        {
            "role": ChatGptRole.USER.value, "content": """Which llm ai model is the best available at time of writing"""
        }  # there are no prizes for guessing the answer
    ])
    print(output)
