import logging
import os
from typing import List, Dict, Any

import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface
from Data.FileManagement import FileManagement
from Personas.PersonaSpecification.PersonaConstants import ADD_TO_ENCYCLOPEDIA_FUNCTION_SCHEMA


class UserEncyclopediaManagement(EncyclopediaManagementInterface):
    """
    **UserEncyclopediaManagement**: A class for managing encyclopedia entries, enabling retrieval,
    updating, and organization of user information.

    This class implements a singleton pattern to ensure only a single instance exists in
    memory. It facilitates the addition and management of user-specific terms
    extracted from interactions.
    """

    ENCYCLOPEDIA_NAME = "UserEncyclopedia"

    instructions = (
        "For the given prompt return an array of things we can now say we know about the user, "
        "as in personal information, *based* on their prompt. "
        "If a user asks for a question that would not benefit from knowing anything about them, don't look up anything"
        "The terms should be as simple as possible, e.g., the actual word of that concept. "
    )

    _instance = None

    def __new__(cls) -> "UserEncyclopediaManagement":
        """Ensures a single instance of UserEncyclopediaManagement."""
        if cls._instance is None:
            cls._instance = super(UserEncyclopediaManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the UserEncyclopediaManagement instance."""
        super().__init__()
        self.encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + ".yaml")
        self.redirect_encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + "Redirects.csv")
        self.load_encyclopedia_data()

    def fetch_term_and_update(self, term_name: str) -> bool:
        """Loads the current state of the user encyclopedia.

        The user encyclopedia is updated more selectively than the general encyclopedia,
        typically based only on user input.

        :param term_name: The name of the term to fetch from the user encyclopedia.
        :return: True if fetching and updating were successful, False otherwise.
        """
        try:
            self.load_encyclopedia_data()

            return True
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Failed to load data for '{term_name}': {e}")
            return False
        except Exception as e:
            logging.exception(f"Unexpected error while trying to fetch '{term_name}': {e}")
            return False

    def add_to_encyclopedia(self, user_input: List[str]) -> None:
        """Review the input user_messages and determine if anything meaningful can be added to the user encyclopedia

        :param user_input: The user input to analyse
        """
        terms = self.extract_terms_from_input(user_input)
        logging.info(f"Extracted terms for {self.ENCYCLOPEDIA_NAME}: {terms}")

        new_entries = self.process_terms(terms)
        if new_entries:
            FileManagement.write_to_yaml(new_entries, self.encyclopedia_path)

    def extract_terms_from_input(self, user_input: List[str]) -> List[Dict[str, Any]]:
        """Extracts terms from user input using AiOrchestrator.

        :param user_input: The input text provided by the user.
        :return: A list of dictionaries containing extracted terms and their respective content.
        """
        executor = AiOrchestrator()
        response = executor.execute_function(
            [self.instructions],
            user_input,
            ADD_TO_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        return response.get('terms', [])

    def process_terms(self, terms: List[Dict[str, Any]]) -> Dict[str, str]:
        """Processes new terms and prepares them for addition to the encyclopedia.

        This method validates each term extracted from user input before adding it to the encyclopedia.

        :param terms: The new terms extracted from user input.
        :return: A dictionary of new terms to be added to the encyclopedia.
        """
        existing_data = FileManagement.load_yaml(self.encyclopedia_path)
        new_entries = {}

        for term_info in terms:
            try:
                key = term_info['term'].strip().lower()  # Ensure the key is case-insensitive
                value = term_info['content']

                if key in existing_data:
                    logging.info(f"Key: [{key}] already present in {self.ENCYCLOPEDIA_NAME}. " +
                                 f"Original: {existing_data.get(key)}, " +
                                 f"Replacement: {value}")
                    continue  # Skip if the key already exists

                self.validate_term(key, value)  # Validate the new term
                logging.info(f"Adding to {self.ENCYCLOPEDIA_NAME} - {key}: {value}")
                new_entries[key] = value  # Add the new key-value pair
            except ValueError as e:
                logging.warning(f"Validation error for term {term_info}: {e}")
            except Exception as e:
                logging.exception(f"Failure to add to {self.ENCYCLOPEDIA_NAME}, for {term_info}: {e}")

        return new_entries

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
    encyclopediaManagement = UserEncyclopediaManagement()
    # print(encyclopediaManagement.search_encyclopedia(["Do you know what my name is?"]))
    encyclopediaManagement.add_to_encyclopedia(
        [
            "Hey my name is Joe, I work as a Backend Software Developer and I'm coding up a ChatGpt Wrapper hobby "
            "project called 'The Thinker'"
        ]
    )
