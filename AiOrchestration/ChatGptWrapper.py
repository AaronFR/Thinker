import enum
import json
import logging
from typing import List, Dict

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion

from Utilities import Globals
from Utilities.ErrorHandler import ErrorHandler


class ChatGptRole(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatGptModel(enum.Enum):
    CHAT_GPT_4_OMNI_MINI = "gpt-4o-mini"
    CHAT_GPT_4_OMNI = "gpt-4o"


class ChatGptWrapper:

    cost_per_input_token_gpt4o_mini = 0.00000015  # $/t
    cost_per_output_token_gpt4o_mini = 0.00000060  # $/t
    cost_per_input_token_gpt4o = 0.000005  # $/t
    cost_per_output_token_gpt4o = 0.000015  # $/t

    def __init__(self):
        ErrorHandler.setup_logging()
        self.open_ai_client = OpenAI()

    def get_open_ai_response(
            self, messages: List[dict], model=ChatGptModel.CHAT_GPT_4_OMNI_MINI, n=1) -> str | List[str]:
        """Request a response from the OpenAI API.

        :param messages: The system and user messages to send to the ChatGpt client
        :param model: the actual llm being called
        :param n: number of times to rerun the prompt
        :return: The content of the response from OpenAI or an error message to inform the next Executor.
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")

            chat_completion = self.open_ai_client.chat.completions.create(
                model=model.value, messages=messages, n=n
            )
            self.calculate_prompt_cost(chat_completion, model)

            responses = [choice.message.content for choice in chat_completion.choices]
            return responses[0] if n == 1 else responses or "[ERROR: NO RESPONSE FROM OpenAI API]"
        except OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def get_open_ai_function_response(self,
                                      messages: List[dict],
                                      function_schema,
                                      model=ChatGptModel.CHAT_GPT_4_OMNI_MINI) -> Dict[str, object]:
        """Requests a structured response from the OpenAI API for function calling.

        :param messages: The system and user messages to send to the ChatGpt client
        :param function_schema:  The schema to apply to the output json
        :param model: the actual llm to call
        :return: The content of the response from OpenAI or an error message to inform the next executor task
        """
        try:
            logging.debug(f"Calling OpenAI API with messages: {messages}")
            chat_completion = self.open_ai_client.chat.completions.create(
                model=model.value,
                messages=messages,
                functions=function_schema,
                function_call={"name": "executiveDirective"}
                # ToDo investigate more roles
            )
            self.calculate_prompt_cost(chat_completion, model)

            logging.info(f"Executive Plan: {chat_completion}")
            arguments = chat_completion.choices[0].message.function_call.arguments
            return json.loads(arguments) if arguments else {"error": "NO RESPONSE FROM OpenAI API"}
        except OpenAIError:
            logging.error(f"OpenAI API error:")
            raise
        except Exception:
            logging.error(f"Unexpected error")
            raise

    def calculate_prompt_cost(self, chat_completion: ChatCompletion, model: ChatGptModel):
        """
        Calculates the estimated cost of a call to OpenAi ChatGpt Api

        :param chat_completion: after the prompt has been processed
        :param model: the specific OpenAI model being used, the non Mini version is *very* expensive,
        and should be used rarely
        """
        input_token_price, output_token_price = 0, 0

        if model == ChatGptModel.CHAT_GPT_4_OMNI_MINI:
            input_token_price = chat_completion.usage.prompt_tokens * self.cost_per_input_token_gpt4o_mini
            output_token_price = chat_completion.usage.completion_tokens * self.cost_per_output_token_gpt4o_mini
        if model == ChatGptModel.CHAT_GPT_4_OMNI:
            logging.warning("EXPENSIVE MODEL USED!")
            input_token_price = chat_completion.usage.prompt_tokens * self.cost_per_input_token_gpt4o_mini
            output_token_price = chat_completion.usage.completion_tokens * self.cost_per_output_token_gpt4o_mini

        Globals.current_request_cost += (input_token_price + output_token_price)

        logging.info(
            f"""Input tokens: {chat_completion.usage.prompt_tokens}, price: ${round(input_token_price, 4)}
            Output tokens: {chat_completion.usage.completion_tokens}, price: ${round(output_token_price, 4)}
            Total cost: ¢{round((input_token_price + output_token_price) * 100, 4)}
        """)


if __name__ == '__main__':
    ChatGptWrapper = ChatGptWrapper()

    output = ChatGptWrapper.get_open_ai_response([
        {
            "role": ChatGptRole.USER.value, "content": """Which llm ai model is the best available at time of writing"""
        }  # there are no prizes for guessing the answer
    ])
    print(output)
