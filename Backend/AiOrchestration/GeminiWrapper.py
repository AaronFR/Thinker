import enum
import json
import logging
import os
from typing import List, Dict, Tuple

from google import genai

from flask_socketio import emit
from google.genai.types import GenerateContentResponse, GenerateContentConfig

from AiOrchestration.ChatGptMessageBuilder import format_message
from AiOrchestration.GeminiModel import GeminiModel
from Constants import Globals
from Constants.Constants import GEMINI_API_KEY
from Utilities.Contexts import get_message_context, get_functionality_context
from Utilities.Decorators import handle_errors
from Utilities.ErrorHandler import ErrorHandler
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB

#  For now assuming that google only has text and vision available


class GeminiRole(enum.Enum):
    """Defines roles in the chat completion interaction."""
    USER = "user"
    SYSTEM = "system"


class CostConfiguration:  #  This entire Class will need refactoring to properly calculate costs
    """Handles cost configuration for API calls."""

    def __init__(self):
        """
        Initialize cost settings from environment variables or defaults.
        """
        # Placeholder costs since Gemini's pricing structure differs significantly from OpenAI's
        self.input_token_costs = {model: float(os.environ.get(f'INPUT_COST_{model.name}', default)) for model, default in {
            GeminiModel.GEMINI_2_FLASH: 0.0000001,  # $/token
            GeminiModel.GEMINI_2_FLASH_LITE_PREVIEW: 0.000000075,  # $/token
        }.items()}

        self.output_token_costs = {model: float(os.environ.get(f'OUTPUT_COST_{model.name}', default)) for model, default in {
            GeminiModel.GEMINI_2_FLASH: 0.0000004,  # $/token
            GeminiModel.GEMINI_2_FLASH_LITE_PREVIEW: 0.00000015,  # $/token
        }.items()}


class GeminiWrapper:
    """Wrapper class for interacting with the Google Gemini API."""

    _instance = None

    def __new__(cls):
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(GeminiWrapper, cls).__new__(cls)
            cls._instance.gemini_client = genai.Client(api_key=os.getenv(GEMINI_API_KEY))
            cls._instance.cost_config = CostConfiguration()  # Load cost configurations
        return cls._instance

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    def _prepare_gemini_messages(messages: List[Dict[str, str]]) -> tuple[
        list[dict[str, str] | dict[str, str]], list[dict[str, str]]]:
        """Converts OpenAI-style messages to Gemini-style messages.

        Args:
            messages: A list of messages in OpenAI format.

        Returns:
            A list of messages in Gemini format.
        """
        user_messages = []
        system_messages = []
        for message in messages:
            role = message['role']
            content = message['content']

            if role == "system":
                system_messages.append({'role': GeminiRole.SYSTEM.value, 'content': content})  # This will handle case when only system prompt is sent in
            elif role == "user":
                user_messages.append({'role': GeminiRole.USER.value, 'content': content})
            elif role == "assistant":
                user_messages.append({
                    'role': GeminiRole.USER.value,
                    'content': "<message_history>\n" + content + "\n</message_history>"
                })
            else:
                logging.warning(f"Unknown message role: {role}")
        return user_messages, system_messages

    def get_ai_response(
            self,
            messages: List[Dict[str, str]],
            model: GeminiModel = GeminiModel.GEMINI_2_FLASH,
            rerun_count: int = 1) -> str | List[str]:
        """Request a response from the Gemini API.

        :param messages: The system and user messages to send to the Gemini client
        :param model: the actual llm being called
        :param rerun_count: number of times to rerun the prompt
        :return: The content of the response from Gemini or an error message to inform the next Executor
        """
        try:
            user_messages, system_messages = self._prepare_gemini_messages(messages)
            prompt = ' '.join([message['content'] for message in user_messages])  # Gemini takes single prompt
            system_instructions = ' '.join([message['content'] for message in system_messages])

            response: GenerateContentResponse = self.gemini_client.models.generate_content(
                model=model.value,
                contents=prompt,
                config=GenerateContentConfig(
                    candidate_count=rerun_count,
                    system_instruction=system_instructions
                )
            )
            # response.candidates[0].content.parts[0].thought worth remembering for later
            outputs = [candidate.content.parts[0].text for candidate in response.candidates]
            output = outputs[0] if rerun_count == 1 else ''.join(outputs)

            self.calculate_prompt_cost(
                self.gemini_client.models.count_tokens(
                    model=model.value,
                    contents=prompt + system_instructions
                ).total_tokens,
                self.gemini_client.models.count_tokens(
                    model=model.value,
                    contents=output
                ).total_tokens,
                model
            )
            return output

        except Exception as e:
            logging.exception("Gemini server failure")
            raise e

    @handle_errors(debug_logging=True, raise_errors=True)
    def get_ai_streaming_response(
            self,
            messages: List[Dict[str, str]],
            model: GeminiModel = GeminiModel.GEMINI_2_FLASH
    ) -> str | List[str]:
        """Request a streaming response from the Gemini API.

        :param messages: The system and user messages to send to the Gemini client
        :param model: the actual llm being called
        :return: The content of the response from Gemini or an error message to inform the next Executor
        """
        try:
            user_messages, system_messages = self._prepare_gemini_messages(messages)
            prompt = ' '.join([message['content'] for message in user_messages])  # Gemini takes single prompt

            system_instructions = None
            if len(system_messages) > 0:
                system_instructions = ' '.join([message['content'] for message in system_messages])

            outputs = self.gemini_client.models.generate_content_stream(
                model=model.value,
                contents=prompt,
                config=GenerateContentConfig(
                    system_instruction=system_instructions if system_instructions.strip() else None
                )
            )
            response_content = []

            for chunk in outputs:
                content = chunk.text
                if content:
                    response_content.append(content)
                    yield {'content': content}  # Streaming text to frontend

            full_response = ''.join(response_content)
            self.calculate_prompt_cost(
                self.gemini_client.models.count_tokens(
                    model=model.value,
                    contents=prompt + system_instructions if system_instructions.strip() else prompt
                ).total_tokens,  # ToDo: You can also retrieve the number of cached tokens
                self.gemini_client.models.count_tokens(
                    model=model.value,
                    contents=full_response
                ).total_tokens,
                model
            )

        except Exception as e:
            emit('response', {'content': str(e)})
            logging.exception("Failed to stream")
        finally:
            yield {'stream_end': True}
            pass

        return full_response

    @handle_errors(debug_logging=True, raise_errors=True)
    def get_ai_function_response(self,
                                 messages: List[Dict[str, str]],
                                 function_schema,
                                 model=GeminiModel.GEMINI_2_FLASH) -> Dict[str, object]:
        """
        Function calling isn't currently supported by Gemini API outside of beta, so for now we just treat them like
        regular calls

        :param messages: Messages sent to the Gemini client
        :param function_schema: Expected schema for the function output
        :param model: The specific language model to use.
        :return: The content of the response from OpenAI or an error message to inform the next executor task
        """
        user_messages, system_messages = self._prepare_gemini_messages(messages)
        prompt = ' '.join([message['content'] for message in user_messages])  # Gemini takes single prompt

        system_messages.extend(format_message(
            GeminiRole.SYSTEM, (
                "Make sure to return your response as a valid json object in accordance directly with the following "
                "schema."
            )
        ))
        system_messages.extend(format_message(
            GeminiRole.SYSTEM, function_schema
        ))  # putting function schema as primary system instruction
        system_instructions = ' '.join([message['content'] for message in system_messages])

        outputs: GenerateContentResponse = self.gemini_client.models.generate_content(
            model=model.value,
            contents=prompt,
            config=GenerateContentConfig(
                system_instruction=system_instructions
            )
        )
        responses = [candidate.content.parts[0].text for candidate in outputs.candidates]
        output = responses[0]

        self.calculate_prompt_cost(
            self.gemini_client.models.count_tokens(
                model=model.value,
                contents=prompt + system_instructions
            ).total_tokens,  # ToDo: You can also retrieve the number of cached tokens
            self.gemini_client.models.count_tokens(
                model=model.value,
                contents=output
            ).total_tokens,
            model
        )

        return json.loads(output) if output else {"error": "NO RESPONSE FROM OpenAI API"}

    def calculate_prompt_cost(self, input_tokens: int, output_tokens: int, model: GeminiModel):
        """Calculates the estimated cost of a call to Gemini Api

        :param input_tokens: prompt tokens
        :param output_tokens: response tokens from the Gemini model
        :param model: the specific Gemini model being used. Placeholders for now
        """
        #  Refactor cost calculation to properly align with gemini costs, its not token based as of December 2024
        input_cost = input_tokens * self.cost_config.input_token_costs[model]
        output_cost = output_tokens * self.cost_config.output_token_costs[model]
        total_cost = (input_cost + output_cost)

        Globals.current_request_cost += total_cost

        NodeDB().deduct_from_user_balance(total_cost)

        message_id = get_message_context()
        if message_id:
            logging.info(f"Expensing ${total_cost} to USER_PROMPT Node[{message_id}]")
            NodeDB().expense_node(message_id, total_cost)
        functionality = get_functionality_context()
        if functionality:
            logging.info(f"Expensing ${total_cost} against {functionality} functionality.")
            NodeDB().expense_functionality(functionality, total_cost)

        logging.info(
            f"Request cost [{model}] - Input tokens: {input_tokens} ${input_cost}, "
            f"Output tokens: {output_tokens}, ${output_cost} "
            f"Total cost: ${total_cost:.4f}"
        )

if __name__ == '__main__':
    """
    This method will fail specifially because the code works within a flask context, disable these calls when testing
    """
    gemini_wrapper = GeminiWrapper()

    # Example usage
    messages = [
        {"role": GeminiRole.USER.value, "content": "Tell me about the capital of France."},
        {"role": GeminiRole.SYSTEM.value, "content": "Nederlands Spreken"},
        {"role": GeminiRole.USER.value, "content": "Who painted the Mona Lisa?"}
    ]

    output = gemini_wrapper.get_ai_response(messages, model=GeminiModel.GEMINI_2_FLASH, rerun_count=1)
    logging.info(f"Gemini Response: {output}")

    # for chunk in gemini_wrapper.get_gemini_streaming_response(messages):
    #     print(chunk)
