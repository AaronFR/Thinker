import logging
import time
from typing import List, Dict, Callable, Any

import tiktoken
from Utilities import Constants
from AiOrchestration.ChatGptWrapper import ChatGptModel


class Utility:

    @staticmethod
    def is_within_token_limit(content: str, limit=128000, model="gpt-4o-mini") -> bool:
        """Check if content size is within token limit."""
        # To get the tokeniser corresponding to a specific model in the OpenAI API:
        enc = tiktoken.encoding_for_model(model)
        token_count = len(enc.encode(content))

        return token_count <= limit

    @staticmethod
    def calculate_tokens_used(messages: List[Dict[str, str]], model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI):
        token_count = 0
        for message in messages:
            enc = tiktoken.encoding_for_model(model.value)
            token_count += len(enc.encode(str(message['content'])))

        return token_count

    @staticmethod
    def execute_with_retries(func: Callable[[], Any], max_retries: int = Constants.MAX_PROMPT_RETRIES) -> Any:
        """Execute a callable with retries on failure.

        :param func: A callable that will be executed
        :param max_retries: Maximum number of retries for the callable
        :return: The return value of the callable if successful, or None if all retries fail
        """
        for attempt in range(max_retries):
            try:
                return func()
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

        if not isinstance(output, list) or not all(isinstance(sp, str) for sp in output):
            raise ValueError("""List is invalid, one or more elements is not a list. 
                    Please ensure compliance with this expected structure for proper functionality.""")

        return output

    @staticmethod
    def is_exit_command(user_input: str) -> bool:
        """Check if the user intends to exit the input loop."""
        return user_input.lower() == 'exit'

    @staticmethod
    def is_valid_question(user_input: str) -> bool:
        """Validate if the user input is a non-empty question."""
        if not user_input.strip():
            print("Please enter a valid question.")
            return False

        return True


if __name__ == '__main__':
    example = "replace_file_clues"
    utility = Utility()
