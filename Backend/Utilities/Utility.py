import logging
import os
import threading
import time
from typing import List, Dict, Callable, Any

import tiktoken
from google import genai

from AiOrchestration.AiModel import AiModel
from AiOrchestration.GeminiModel import GeminiModel
from AiOrchestration.ChatGptModel import ChatGptModel
from Constants import Constants
from Constants.Constants import GEMINI_API_KEY


class Utility:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Create a new instance or return the existing one."""
        if not cls._instance:
            with cls._lock:  # Ensure thread-safety during instance creation
                if not cls._instance:  # Double-check to avoid race conditions
                    cls._instance = super(Utility, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'gemini_client'):
            self.gemini_client = genai.Client(api_key=os.getenv(GEMINI_API_KEY))

    @staticmethod
    def is_within_token_limit(content: str, limit=128000, model="gpt-4o-mini") -> bool:
        """Check if content size is within token limit."""
        # To get the tokeniser corresponding to a specific model in the OpenAI API:
        enc = tiktoken.encoding_for_model(model)
        token_count = len(enc.encode(content))

        return token_count <= limit

    @staticmethod
    def encapsulate_in_tag(content: str, tag: str):
        """
        Surround the content in a HTML-like tag, not just for html, AI frequently understands what the content is better
        contextually
        when surrounded by similar tags

        :param content: The content to encapsulate with the tag
        :param tag: The 'tag' representing a HTML element
        :return: surrounded by html tags
        """
        return f"<{tag}>\n{content}\n</{tag}>"

    def calculate_tokens_used(self, messages: List[Dict[str, str]], model: AiModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI):
        token_count = 0
        model_type = type(model)

        if model_type == ChatGptModel:
            enc = tiktoken.encoding_for_model(model.value)
            for message in messages:
                token_count += len(enc.encode(str(message['content'])))

        if model_type == GeminiModel:
            character_soup = ""
            for message in messages:
                character_soup += message.get("content")
            token_count = self.gemini_client.models.count_tokens(
                model=model.value,
                contents=character_soup
            ).total_tokens.bit_count()

        return token_count

    @staticmethod
    def execute_with_retries(func: Callable[[], Any], max_retries: int = Constants.MAX_PROMPT_RETRIES) -> Any:
        """
        Execute a callable with retries on failure or None result
        (not suitable for methods that can return None for a successful operation)

        :param func: A callable that will be executed
        :param max_retries: Maximum number of retries for the callable
        :return: The return value of the callable if successful, or None if all retries fail
        """
        for attempt in range(1, max_retries + 1):
            try:
                result = func()
                if not result:
                    raise Exception("Function failed to return result")
                else:
                    return result
            except Exception as e:
                wait_time = Constants.BACKOFF_INITIAL ** attempt  # Exponential backoff
                logging.exception(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)  # Wait before retrying
        logging.error("Max retries exceeded. Failed to get response from callable.")
        return None

    @staticmethod
    def ensure_string_list(list_or_string: list[object] | str):
        if isinstance(list_or_string, str):
            logging.warning("""Had to reformat a string into a list, this can lead to strings being decomposed into 
                            individual characters if not correctly handled""")
            output = [list_or_string]
        else:
            output = list_or_string

        if not isinstance(output, list):
            raise ValueError(
                f"The supplied parameter is a {type(list_or_string)} not a list.\n"
                 "Please ensure compliance with this expected structure for proper functionality.)"
            )
        if not all(isinstance(sp, str) for sp in output):
            for sp in output:
                if not isinstance(sp, str):
                    raise ValueError(
                        f"INVALID: {sp} element is a {type(sp)} not a string!\n"
                        "Please ensure compliance with this expected structure for proper functionality."
                    )

        return output

    @staticmethod
    def is_valid_prompt(user_input: str) -> bool:
        """Validate if the user input is a non-empty question."""
        if not user_input.strip():
            logging.error("Invalid prompt entered")
            return False

        return True


if __name__ == '__main__':
    example = "replace_file_clues"
    utility = Utility()
