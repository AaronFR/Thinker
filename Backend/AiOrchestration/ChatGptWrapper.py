import enum
import json
import logging
from typing import List, Dict

from deprecated.classic import deprecated
from flask_socketio import emit
from openai import OpenAI, BadRequestError

from AiOrchestration.AiWrapper import AiWrapper
from AiOrchestration.ChatGptModel import ChatGptModel
from Constants.Constants import CANNOT_AFFORD_REQUEST
from Constants.Exceptions import OPEN_AI_FLAGGED_REQUEST_INAPPROPRIATE, \
    SERVER_FAILURE_OPEN_AI_API, FAILURE_TO_STREAM
from Utilities.Decorators import handle_errors
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Utility import Utility


class ChatGptRole(enum.Enum):
    """Defines roles in the chat completion interaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatGptWrapper(AiWrapper):

    _instance = None

    def __new__(cls):
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(ChatGptWrapper, cls).__new__(cls)
            cls._instance.open_ai_client = OpenAI()  # Initialize the OpenAI client
        return cls._instance

    def __init__(self):
        ErrorHandler.setup_logging()

    def get_ai_response(
            self,
            messages: List[Dict[str, str]],
            model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
            rerun_count: int = 1) -> str | List[str]:
        """Request a response from the OpenAI API.

        :param messages: The system and user messages to send to the ChatGpt client
        :param model: the actual llm being called
        :param rerun_count: number of times to rerun the prompt
        :return: The content of the response from OpenAI or an error message to inform the next Executor
        """
        if not self.can_afford_request(model, messages, rerun_count):
            return CANNOT_AFFORD_REQUEST

        try:
            chat_completion = self.open_ai_client.chat.completions.create(
                model=model.value, messages=messages, n=rerun_count
            )
            self.calculate_prompt_cost(
                chat_completion.usage.prompt_tokens,
                chat_completion.usage.completion_tokens,
                model
            )
        except BadRequestError:
            logging.exception(OPEN_AI_FLAGGED_REQUEST_INAPPROPRIATE)
            return "OpenAi ChatGpt Server Flagged Your Request as Inappropriate. Try again, it does this alot."
        except Exception as e:
            logging.exception(SERVER_FAILURE_OPEN_AI_API)
            raise e

        responses = [choice.message.content for choice in chat_completion.choices]
        return responses[0] if rerun_count == 1 else responses or None

    @handle_errors(debug_logging=True, raise_errors=True)
    def get_ai_streaming_response(
            self,
            messages: List[Dict[str, str]],
            model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI) -> str | List[str]:
        """Request a response from the OpenAI API with streaming enabled and calculate cost at the end.

        :param messages: The system and user messages to send to the ChatGPT client
        :param model: the actual llm being called
        :return: The content of the response from OpenAI or an error message to inform the next Executor
        """
        if not self.can_afford_request(model, messages):
            return CANNOT_AFFORD_REQUEST

        try:
            response_content = []

            chat_completion = self.open_ai_client.chat.completions.create(
                model=model.value,
                messages=messages,
                stream=True
            )

            for chunk in chat_completion:
                delta = chunk.choices[0].delta
                content = getattr(delta, 'content', None)

                if content:
                    response_content.append(content)
                    yield {'content': content}

                # ToDo: Check for user termination condition here
                # if user_requested_stop():  # Placeholder for actual stop condition
                #     user_terminated = True
                #     break  # Exit the loop if user interrupts

            # Combine all parts of the response for final cost calculation
            full_response = ''.join(response_content)
            final_message = [{"content": full_response}]
            self.calculate_prompt_cost(
                Utility().calculate_tokens_used(messages, model),
                Utility().calculate_tokens_used(final_message, model),
                model
            )
        except Exception as e:
            emit('response', {'content': e})
            logging.exception(FAILURE_TO_STREAM)
        finally:
            yield {'stream_end': True}
        # ToDo: ideally workflow_step_finished events should be sent here
        #  Could change the prior event to 'Streaming' and this new one to complete

        return full_response

    @deprecated
    @handle_errors(debug_logging=True, raise_errors=True)
    def get_ai_function_response(self,
                                 messages: List[Dict[str, str]],
                                 function_schema,
                                 model=ChatGptModel.CHAT_GPT_4_OMNI_MINI) -> Dict[str, object]:
        """Requests a structured response from the OpenAI API for function calling.

        :param messages: Messages sent to the ChatGPT client
        :param function_schema: Expected schema for the function output
        :param model: The specific language model to use.
        :return: The content of the response from OpenAI or an error message to inform the next executor task
        """
        if not self.can_afford_request(model, messages):
            return CANNOT_AFFORD_REQUEST

        if model == ChatGptModel.CHAT_GPT_O1_MINI or model == ChatGptModel.CHAT_GPT_O3_MINI:
            raise Exception("O1 models do not support function calls!")
        chat_completion = self.open_ai_client.chat.completions.create(
            model=model.value,
            messages=messages,
            functions=function_schema,
            function_call={"name": "executiveDirective"}
        )
        self.calculate_prompt_cost(
            chat_completion.usage.prompt_tokens,
            chat_completion.usage.completion_tokens,
            model
        )

        arguments = chat_completion.choices[0].message.function_call.arguments
        return json.loads(arguments) if arguments else {"error": SERVER_FAILURE_OPEN_AI_API}


if __name__ == '__main__':
    ChatGptWrapper = ChatGptWrapper()

    # output = ChatGptWrapper.get_open_ai_response([
    #     {
    #         "role": ChatGptRole.USER.value, "content": """Which llm ai model is the best available at time of writing"""
    #     }  # there are no prizes for guessing the answer
    # ])
    output = ChatGptWrapper.get_ai_streaming_response([
        {
            "role": ChatGptRole.USER.value, "content": "Describe Spain?",
        },
        {
            "role": ChatGptRole.ASSISTANT.value, "content": "Whats the capital of France?"
        },
        {
            "role": ChatGptRole.ASSISTANT.value, "content": "My name is joe"
        },
        {
            "role": ChatGptRole.SYSTEM.value, "content": "You will answer responses in Chinese"
        },
        {
            "role": ChatGptRole.SYSTEM.value, "content": "You will answer responses in Portuguese"
        }
    ])
    logging.info(f"Output, {output}")
