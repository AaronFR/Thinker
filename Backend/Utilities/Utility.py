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

    def calculate_tokens_used(
        self, messages: List[Dict[str, str]], model: AiModel = ChatGptModel.CHAT_GPT_4_POINT_ONE_NANO
    ):
        token_count = 0
        model_type = type(model)

        # Each message might have additional tokens for formatting.
        # For instance, OpenAI documentation notes that there are usually extra tokens per message.
        # The exact count varies, but assume a base count per message (e.g., 4 tokens per message).
        extra_tokens_per_message = 4

        if model_type == ChatGptModel:
            try:
                encoding = tiktoken.encoding_for_model(model.value)
            except KeyError:
                # If the model name isn't recognized, fall back to the likely encoding
                logging.warning(
                    f"Could not automatically map model '{model.value}' to a tokenizer. "
                    f"Falling back to 'cl100k_base' encoding. Please update 'tiktoken' "
                    f"library when a new version is available."
                )
                encoding = tiktoken.get_encoding("cl100k_base")

            for message in messages:
                token_count += len(encoding.encode(message.get("content", "")))
                token_count += extra_tokens_per_message

            # Depending on the API’s wrapping of the conversation prompt,
            # you might need to account for additional tokens.
            # For example, if there's an overall prefix or suffix added to the conversation.
            overall_extra_tokens = 2
            token_count += overall_extra_tokens

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
        (not suitable for methods that can return None or False for a successful operation)

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


if __name__ == '__main__':
    example = "replace_file_clues"
    utility = Utility()
