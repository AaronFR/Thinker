import logging
import re

from typing import List, Dict, Any

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities.Instructions import extract_memory_node_terms_system_message, PARSE_MEMORY_NODES_SYSTEM_MESSAGE

ENCYCLOPEDIA_NAME = "User Context"


class UserContextManagement(EncyclopediaManagementInterface):
    """
    UserContextManagement: A class for managing user-specific terms
    extracted from interactions, enabling retrieval of user context.

    This class implements a singleton pattern to ensure only a single
    instance exists in memory.
    """

    _instance = None
    # Precompiled regex pattern for extracting user topic tags
    TAG_PATTERN = re.compile(
        r'<(?P<node_name>[a-zA-Z_]+)\s+parameter="(?P<parameter>[^"]+)"\s+content="(?P<content>[^"]+)"\s*/>'
    )

    def __init__(self):
        super().__init__()
        self.instructions = PARSE_MEMORY_NODES_SYSTEM_MESSAGE

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
        existing_nodes = NodeDB().list_user_topics()

        try:
            user_topics_reasoning = AiOrchestrator().execute(
                [extract_memory_node_terms_system_message(existing_nodes)],
                user_input,
            )
            logging.info(f"User topic reasoning: {user_topics_reasoning}")

            parsed_terms = UserContextManagement.parse_user_topic_tags(user_topics_reasoning)
            logging.info(f"Parsed terms: {parsed_terms}")
            return parsed_terms

        except Exception as e:
            logging.exception("Failed to extract terms from user input.", exc_info=e)
            return []

    @staticmethod
    def parse_user_topic_tags(input_text: str) -> List[Dict[str, str]]:
        """Parses user topic tags from the input text.

        :param input_text: A string containing user topic tags to parse.
        :return: A list of dictionaries with node names, parameters, and content.
        """
        matches = UserContextManagement.TAG_PATTERN.findall(input_text)  # Extract all matches from input_text

        if not matches:
            logging.warning("No matches found for user topic tags.")

        tags = [{
            "node": match[0],
            "parameter": match[1],
            "content": match[2]
        } for match in matches]

        return tags

    @staticmethod
    def validate_term(key: str, value: str) -> None:
        """
        Validates the term before adding it to the encyclopedia.
        Ensuring the key and value are not empty or exceed predefined lengths.

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
