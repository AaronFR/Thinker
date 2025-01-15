import enum
import json
import logging
import os
from typing import List, Dict

from flask_socketio import emit
from openai import OpenAI, BadRequestError

from AiOrchestration.ChatGptModel import ChatGptModel
from Utilities import Globals
from Utilities.Contexts import get_expensed_nodes, set_expensed_nodes
from Utilities.Decorators import handle_errors
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Utility import Utility
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB


class ChatGptRole(enum.Enum):
    """Defines roles in the chat completion interaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class CostConfiguration:
    """Handles cost configuration for API calls."""

    def __init__(self):
        """
        Initialize cost settings from environment variables or defaults.
        """
        self.input_token_costs = {model: float(os.environ.get(f'INPUT_COST_{model.name}', default)) for model, default in {
            ChatGptModel.CHAT_GPT_4_OMNI_MINI: 0.00000015,  # $/token
            ChatGptModel.CHAT_GPT_4_OMNI: 0.0000025,  # $/token
            ChatGptModel.CHAT_GPT_O1_MINI: 0.000003,  # $/token
            ChatGptModel.CHAT_GPT_O1_PREVIEW: 0.000015,  # $/token
        }.items()}

        self.output_token_costs = {model: float(os.environ.get(f'OUTPUT_COST_{model.name}', default)) for model, default in {
            ChatGptModel.CHAT_GPT_4_OMNI_MINI: 0.0000006,  # $/token
            ChatGptModel.CHAT_GPT_4_OMNI: 0.00001,  # $/token
            ChatGptModel.CHAT_GPT_O1_MINI: 0.000012,  # $/token
            ChatGptModel.CHAT_GPT_O1_PREVIEW: 0.00006,  # $/token
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

    def __init__(self):
        ErrorHandler.setup_logging()

    @handle_errors(debug_logging=True, raise_errors=True)
    def get_open_ai_response(
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
        chat_completion = self.open_ai_client.chat.completions.create(
            model=model.value, messages=messages, n=rerun_count
        )
        self.calculate_prompt_cost(
            chat_completion.usage.prompt_tokens,
            chat_completion.usage.completion_tokens,
            model
        )

        responses = [choice.message.content for choice in chat_completion.choices]
        return responses[0] if rerun_count == 1 else responses or None

    @handle_errors(debug_logging=True, raise_errors=True)
    def get_open_ai_streaming_response(
            self,
            messages: List[Dict[str, str]],
            model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI) -> str | List[str]:
        """Request a response from the OpenAI API with streaming enabled and calculate cost at the end.

        :param messages: The system and user messages to send to the ChatGPT client
        :param model: the actual llm being called
        :return: The content of the response from OpenAI or an error message to inform the next Executor
        """
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
            Utility.calculate_tokens_used(messages, model),
            Utility.calculate_tokens_used(final_message, model),
            model
        )

        yield {'stream_end': True}
        # ToDo: ideally workflow_step_finished events should be sent here
        #  Could change the prior event to 'Streaming' and this new one to complete

        return full_response

    @handle_errors(debug_logging=True, raise_errors=True)
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
        if model == ChatGptModel.CHAT_GPT_O1_MINI or model == ChatGptModel.CHAT_GPT_O1_PREVIEW:
            raise Exception("O1 models do not support function calls!")
        chat_completion = self.open_ai_client.chat.completions.create(
            model=model.value,
            messages=messages,
            functions=function_schema,
            function_call={"name": "executiveDirective"}
            # ToDo:investigate more roles
        )
        self.calculate_prompt_cost(
            chat_completion.usage.prompt_tokens,
            chat_completion.usage.completion_tokens,
            model
        )

        arguments = chat_completion.choices[0].message.function_call.arguments
        return json.loads(arguments) if arguments else {"error": "NO RESPONSE FROM OpenAI API"}

    def calculate_prompt_cost(self, input_tokens: int, output_tokens: int, model: ChatGptModel):
        """Calculates the estimated cost of a call to OpenAi ChatGpt Api

        :param input_tokens: prompt tokens
        :param output_tokens: response tokens from the openAi model
        :param model: the specific OpenAI model being used, the non Mini version is *very* expensive,
        and should be used rarely
        """
        input_cost = input_tokens * self.cost_config.input_token_costs[model]
        output_cost = output_tokens * self.cost_config.output_token_costs[model]
        total_cost = (input_cost + output_cost)
        Globals.current_request_cost += total_cost

        NodeDB().deduct_from_user_balance(total_cost)

        expensed_nodes = get_expensed_nodes()
        for expensed_node_uuid in expensed_nodes:
            logging.info(f"Expensing ${total_cost} to Node[{expensed_node_uuid}]")
            NodeDB().expense_node(expensed_node_uuid, total_cost)
        set_expensed_nodes([])  # wipe after transactions have been expensed

        logging.info(
            f"Request cost [{model}] - Input tokens: {input_tokens}, Output tokens: {output_tokens}, "
            f"Total cost: ${total_cost:.4f}"
        )


if __name__ == '__main__':
    ChatGptWrapper = ChatGptWrapper()

    # output = ChatGptWrapper.get_open_ai_response([
    #     {
    #         "role": ChatGptRole.USER.value, "content": """Which llm ai model is the best available at time of writing"""
    #     }  # there are no prizes for guessing the answer
    # ])
    output = ChatGptWrapper.get_open_ai_streaming_response([
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
