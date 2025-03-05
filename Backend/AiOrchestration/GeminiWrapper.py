import enum
import json
import logging
import os
from typing import List, Dict

from deprecated.classic import deprecated
from google import genai

from flask_socketio import emit
from google.genai.types import GenerateContentResponse, GenerateContentConfig

from AiOrchestration.AiWrapper import AiWrapper
from AiOrchestration.ChatGptMessageBuilder import format_message
from AiOrchestration.GeminiModel import GeminiModel
from Constants.Constants import GEMINI_API_KEY, CANNOT_AFFORD_REQUEST
from Constants.Exceptions import FAILURE_TO_STREAM, SERVER_FAILURE_GEMINI_API, NO_RESPONSE_GEMINI_API
from Utilities.Decorators import handle_errors
from Utilities.PaymentDecorators import evaluate_gemini_balance
from Utilities.ErrorHandler import ErrorHandler


#  For now assuming that google only has text and vision available


class GeminiRole(enum.Enum):
    """Defines roles in the chat completion interaction."""
    USER = "user"
    SYSTEM = "system"


class GeminiWrapper(AiWrapper):
    """Wrapper class for interacting with the Google Gemini API."""

    _instance = None

    def __new__(cls):
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(GeminiWrapper, cls).__new__(cls)
            cls._instance.gemini_client = cls._get_google_genai_client()
        return cls._instance

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    def _get_google_genai_client():
        try:
            return genai.Client(api_key=os.getenv(GEMINI_API_KEY))
        except Exception:
            logging.exception("Failed to create google AI client!")

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
                # This will handle case when only system prompt is sent in
                system_messages.append({'role': GeminiRole.SYSTEM.value, 'content': content})
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

    @evaluate_gemini_balance()
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
        if not self.can_afford_request(model, messages, rerun_count):
            return CANNOT_AFFORD_REQUEST

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
            logging.exception(SERVER_FAILURE_GEMINI_API)
            raise e

    @evaluate_gemini_balance()
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
        if not self.can_afford_request(model, messages):
            return CANNOT_AFFORD_REQUEST

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
            logging.exception(FAILURE_TO_STREAM)
        finally:
            pass

        return full_response

    @deprecated
    @handle_errors(debug_logging=True, raise_errors=True)
    @evaluate_gemini_balance()
    def get_ai_function_response(
        self,
        messages: List[Dict[str, str]],
        function_schema,
        model=GeminiModel.GEMINI_2_FLASH
    ) -> Dict[str, object]:
        """
        Function calling isn't currently supported by Gemini API outside of beta, so for now we just treat them like
        regular calls

        :param messages: Messages sent to the Gemini client
        :param function_schema: Expected schema for the function output
        :param model: The specific language model to use.
        :return: The content of the response from OpenAI or an error message to inform the next executor task
        """
        if not self.can_afford_request(model, messages):
            return CANNOT_AFFORD_REQUEST

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

        return json.loads(output) if output else {"error": NO_RESPONSE_GEMINI_API}


if __name__ == '__main__':
    """
    This method will fail specifically because the code works within a flask context, disable these calls when testing
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
