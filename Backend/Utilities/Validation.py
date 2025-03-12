import logging
import re

import tiktoken


def check_valid_uuid(uuid: str):
    return len(uuid) == 22


def space_in_content(content: str):
    """
    In many separate data schemas a space within the field is invalid
    """
    if ' ' in content:
        return True

    return False


def sanitise_identifier(identifier: str) -> str:
    """
    Sanitizes a dynamic identifier (e.g. label or property name) by
    allowing only alphanumeric characters and underscores.

    ToDo: Confirm this doesn't create an issue in alphabet systems other than Latin.

    Warning: Only use this when you absolutely need to embed
    dynamic identifiers into your Cypher query strings.
    """
    # This regex replaces any character that is NOT alphanumeric or underscore with an underscore
    return re.sub(r'\W', '_', identifier)


# User Prompts

def is_valid_prompt(user_input: str) -> bool:
    """Validate if the user input is a non-empty string."""
    if not user_input.strip():
        logging.error("Invalid prompt entered")
        return False

    return True


def is_within_token_limit(content: str, limit=128000, model="gpt-4o-mini") -> bool:
    """
    Check if content size is within token limit.
    ToDo: Not currently used
    """
    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    enc = tiktoken.encoding_for_model(model)
    token_count = len(enc.encode(content))

    return token_count <= limit


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