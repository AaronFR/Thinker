import logging
import os
import pandas as pd
import yaml

from typing import List, Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING
from Utilities.Decorators import handle_errors


class EncyclopediaManagementInterface:
    """Manages encyclopedia data files and provides search and retrieval capabilities.

    This class facilitates loading encyclopedia entries and redirects, searching for terms,
    and summarizing information relevant to user queries.
    """

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    ENCYCLOPEDIA_NAME = "To Define"
    instructions = "To Define"

    _instance = None

    def __new__(cls) -> 'EncyclopediaManagementInterface':
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagementInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the EncyclopediaManagementInterface."""
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.encyclopedia: Dict[str, str] = {}
            self.redirects: Dict[str, str] = {}

            self.encyclopedia_path = "To Define"
            self.redirect_encyclopedia_path = "To Define"

            self.data_path = os.path.join(os.path.dirname(__file__), '../../UserData/DataStores')
            self.initialized = True

    @handle_errors()
    def load_encyclopedia_data(self) -> None:
        """Load encyclopedia and redirect data from the specified files."""
        self.encyclopedia = self._load_yaml_file(self.encyclopedia_path)
        self.redirects = self._load_redirects(self.redirect_encyclopedia_path)
        logging.info("Encyclopedia and redirects loaded successfully.")

    @staticmethod
    @handle_errors(raise_errors=True)
    def _load_yaml_file(filepath: str) -> Dict[str, str]:
        """Load a YAML file and return its content as a dictionary.

        :param filepath: Path to the YAML file to load.
        :return: Dictionary containing the file contents.
        """
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as file:
            return yaml.safe_load(file) or {}

    @staticmethod
    @handle_errors(raise_errors=True)
    def _load_redirects(filepath: str) -> Dict[str, str]:
        """Load redirect terms from a CSV file and return them as a dictionary.

        :param filepath: Path to the CSV file containing redirects.
        :return: Dictionary mapping redirect terms to target terms.
        """
        redirects_df = pd.read_csv(filepath, header=None, names=['redirect_term', 'target_term'])
        return redirects_df.set_index('redirect_term')['target_term'].to_dict()

    @handle_errors(raise_errors=True)
    def search_encyclopedia(self, user_messages: List[str]) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: List of user input messages containing the terms.
        :return: A string representation of the additional context found.
        """
        output = AiOrchestrator().execute_function(
            [self.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"Terms to search for in {self.ENCYCLOPEDIA_NAME}: {terms}")

        return self.extract_terms_from_encyclopedia(terms)

    def extract_terms_from_encyclopedia(self, terms: List[Dict[str, str]]) -> str:
        """Search for a set of terms in the encyclopedia and return additional context.

        :param terms: The terms to check in the encyclopedia.
        :return: A string representation of additional context extracted.
        """
        additional_context = []

        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                user_topics = nodeDB().list_user_topics()

                selected_topic_raw = AiOrchestrator().execute(
                    ["Given the list of topics I gave you, just return the most appropriate from the list"],
                    [term.get("term") + " : " + term.get("specifics"), str(user_topics)]
                )
                selected_topic = selected_topic_raw.strip("'")

                content = nodeDB().search_for_user_topic_content(selected_topic)
                if content:
                    additional_context.append(content)

            except Exception as e:
                logging.exception(f"Error while trying to access {self.ENCYCLOPEDIA_NAME}: {term_name}", exc_info=e)

        return str(additional_context)

    def selectively_process_entry(self, term_name: str, specifics: str) -> str:
        """Processes a specific encyclopedia entry to summarise information.

        :param term_name: The term to search for in encyclopedia data.
        :param specifics: The specifics about what to explore regarding the term.
        :return: A summarised version of the encyclopedia file content.
        """
        entry_dict = self.encyclopedia.get(term_name)
        output = AiOrchestrator().execute(
            [
                "summarise the following information while retaining essential details."
            ],
            [
                term_name + ": " + specifics,
                str(entry_dict)
            ]
        )

        return output

    def fetch_term_and_update(self, term_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        :param term_name: The name of the term to fetch from Wikipedia.
        :return: A status indicating whether the fetching and updating were successful.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


if __name__ == '__main__':
    pass
