import logging
import re
from pathlib import Path
from typing import List, Dict

import tiktoken
import Constants

logging.basicConfig(level=logging.INFO)

class Utility:

    @staticmethod
    def is_within_token_limit(content: str, limit=128000, model="gpt-4o-mini") -> bool:
        """Check if content size is within token limit.
        """
        # To get the tokeniser corresponding to a specific model in the OpenAI API:
        enc = tiktoken.encoding_for_model(model)
        token_count = len(enc.encode(content))

        return token_count <= limit

    @staticmethod
    def calculate_tokens_used(messages: List[Dict[str, str]], model="gpt-4o-mini"):
        token_count = 0
        for message in messages:
            enc = tiktoken.encoding_for_model(model)
            token_count += len(enc.encode(str(message.get('content'))))

        return token_count


    @staticmethod
    def fill_placeholders(prompt: str) -> str:
        """Replace placeholders in prompt with actual file content if within token limit."""
        file_references = re.findall(Constants.FIND_SQUARE_BRACKET_CLUE_REGEX, prompt)

        for original_file_name in file_references:
            file_name = original_file_name.replace(" ", "_")
            if not Utility.has_file_prefix(file_name):
                file_name += ".txt"
            file_path = Path(file_name)

            try:
                with file_path.open('r', encoding='utf-8') as file:
                    file_content = file.read()

                if Utility.is_within_token_limit(file_content):
                    prompt = prompt.replace(f"[{original_file_name}]", file_content)  # Replace the clue with the actual file content
                else:
                    logging.warning(f"FILE TOO LARGE: {file_name} exceeds token limit")
                    continue  # Skip replacing this file content if it exceeds limit
            except FileNotFoundError:
                logging.error(f"Cannot find file {file_name}")
            except Exception as e:
                logging.error(f"Cannot read file {file_name}: {e}")

        return prompt

    @staticmethod
    def has_file_prefix(clue: str) -> bool:
        # Define the regex pattern to detect file prefixes
        file_prefix_pattern = r'.*\.\w{2,4}'

        match = re.match(file_prefix_pattern, clue.strip())
        return bool(match)


if __name__ == '__main__':
    example = "replace_file_clues"
    utility = Utility()