import enum
import json
import logging
from typing import List, Dict

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion

from Utilities import Globals
from Utilities.ErrorHandler import ErrorHandler


class ChatGptRole(enum.Enum):
    """Defines roles in the chat completion interaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatGptModel(enum.Enum):
    """OpenAI API Models"""
    CHAT_GPT_4_OMNI_MINI = "gpt-4o-mini"
    CHAT_GPT_4_OMNI = "gpt-4o"


class ChatGptWrapper:
    # ToDo: This class can be a singleton it doesn't need to recreate the api for each call

    COST_PER_INPUT_TOKEN_GPT4O_MINI = 0.00000015  # $/t
    COST_PER_OUTPUT_TOKEN_GPT4O_MINI = 0.00000060  # $/t
    COST_PER_INPUT_TOKEN_GPT4O = 0.000005  # $/t
    COST_PER_OUTPUT_TOKEN_GPT4O = 0.000015  # $/t

    def __init__(self):
        ErrorHandler.setup_logging()
        self.open_ai_client = OpenAI()

    def get_open_ai_response(
            self,
            messages: List[Dict[str, str]],
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI,
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
            return responses[0] if rerun_count == 1 else responses or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except OpenAIError as e:
            logging.exception(f"OpenAI API error", e)
            raise
        except Exception as e:
            logging.exception(f"Unexpected error", e)
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

        if model == ChatGptModel.CHAT_GPT_4_OMNI_MINI:
            cost_input = input_tokens * self.COST_PER_INPUT_TOKEN_GPT4O_MINI
            cost_output = output_tokens * self.COST_PER_OUTPUT_TOKEN_GPT4O_MINI
        elif model == ChatGptModel.CHAT_GPT_4_OMNI:
            logging.warning("Using the EXPENSIVE model: CHAT_GPT_4_OMNI")
            cost_input = input_tokens * self.COST_PER_INPUT_TOKEN_GPT4O
            cost_output = output_tokens * self.COST_PER_OUTPUT_TOKEN_GPT4O

        total_cost = cost_input + cost_output
        Globals.current_request_cost += total_cost

        logging.info(
            f"Input tokens: {input_tokens}, Input cost: ${cost_input:.4f}, "
            f"Output tokens: {output_tokens}, Output cost: ${cost_output:.4f}, "
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
