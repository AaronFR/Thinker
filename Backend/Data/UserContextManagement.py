import logging
import re

from typing import List, Dict, Any

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface


class UserContextManagement(EncyclopediaManagementInterface):
    """
    **UserContextManagement**: A class for managing encyclopedia entries, enabling retrieval,
    updating, and organization of user information.

    This class implements a singleton pattern to ensure only a single instance exists in
    memory. It facilitates the addition and management of user-specific terms
    extracted from interactions.
    """

    _instance = None

    def __new__(cls) -> "UserContextManagement":
        """Ensures a single instance of UserContextManagement."""
        if cls._instance is None:
            cls._instance = super(UserContextManagement, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def extract_terms_from_input(user_input: List[str]) -> List[Dict[str, Any]]:
        """Extracts user_topic contextual information based on the users information
        ToDo: The parameters should be all in lowercase
        ToDo: parameters should be plural by default
        ToDo: beneficial to have separate instructions based on context, e.g. personal context versus situational

        :param user_input: The input text provided by the user.
        :return: A list of dictionaries containing extracted terms and their respective content.
        """

        instructions = (
            "For the given prompt, explain your reasoning step by step. "
            "Identify and return an array of specific, concise items that describe personal context that can be inferred"
            "Only infer information if it seems beneficial to the user’s question or future questions. "
            "node_name and parameter are ideally singular words, failing that they must have underscores not spaces - "
            "you chosen name should also get to the root semantic concept rather than focus on specifics. "
            "Then, finally write the potential user topics as "
            "<your_selected_single_word_node_name parameter=\"(your_selected_single_word_parameter_name)\" "
            "content=\"(the content you want to note)\" />"
            "Required: tag name, parameter, content, all 3 must be included"
        )
        user_topics_reasoning = AiOrchestrator().execute(
            [instructions],
            user_input,
        )
        logging.info(f"user topic reasoning : {user_topics_reasoning}")

        parsed_terms = UserContextManagement.parse_user_topic_tags(user_topics_reasoning)
        logging.info(f"parsed terms : {parsed_terms}")
        return parsed_terms

    @staticmethod
    def parse_user_topic_tags(input_text):
        # Define a regular expression to capture node_name, parameter, and content values
        # pattern = r'<\s*(?P<node_name>\w+)\s+parameter\s*=\s*"(?P<parameter>[^"]+)"\s+content\s*=\s*"(?P<content>[^"]+)"\s*/?>'
        pattern = r'<(?P<node_name>[a-zA-Z_]+)\s+parameter="(?P<parameter>[^"]+)"\s+content="(?P<content>[^"]+)"\s*/>'

        matches = list(re.finditer(pattern, input_text))  # Convert to list for easy checking

        if not matches:
            logging.warning("No matches found.")

        tags = [
            {
                "node": match.group("node_name"),
                "parameter": match.group("parameter"),
                "content": match.group("content")
            }
            for match in matches
        ]

        return tags

    @staticmethod
    def validate_term(key: str, value: str) -> None:
        """Validates the term before adding it to the encyclopedia.

        :param key: The key of the term to validate.
        :param value: The content associated with the term.
        :raises ValueError: If the key or value is deemed invalid.
        """
        if not key or not value:
            raise ValueError("Term key and value cannot be empty.")
        if len(key) > 100:  # Arbitrary length restriction
            raise ValueError("Term key is too long.")
        if len(value) > 50000:  # Arbitrary content restriction
            raise ValueError("Term content is too long.")


if __name__ == '__main__':
    encyclopediaManagement = UserContextManagement()
    text = r"""
    <user_name parameter="first_name" content="Johnn" />
    <user_name parameter="last_name" content="James" />
    <user_name parameter="gender" content="male" />
    """
    print(encyclopediaManagement.parse_user_topic_tags(text))
    # print(encyclopediaManagement.extract_terms_from_input(["My name is John James"]))
    # print(encyclopediaManagement.find_terms_for_input(["Do you know what my name is?"]))
