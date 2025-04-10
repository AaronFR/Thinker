import ast
import logging
import re

import pandas as pd
import yaml

from typing import List, Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Exceptions import NOT_IMPLEMENTED_IN_INTERFACE
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Constants.Constants import DEFAULT_ENCODING, EXTRACT_LIST_REGEX
from Utilities.Decorators.Decorators import handle_errors, specify_functionality_context
from Constants.Instructions import select_topic_prompt, SELECT_TOPIC_SYSTEM_MESSAGE, \
    SUMMARISE_WHILE_RETAINING_DETAIL_SYSTEM_MESSAGE, string_of_existing_topics_prompt, SCHEMA_FOR_CONCEPT_TERMS


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
    @specify_functionality_context("user_context")
    def search_encyclopedia(self, user_messages: List[str]) -> str | None:
        """Searches the encyclopedia for terms derived from user messages.

        ToDo: Only user context will be using this interface from now on, at a later stage it needs to be refactored
         away

        :param user_messages: List of user input messages containing the terms.
        :return: A string representation of the additional context found.
        """

        output = AiOrchestrator().execute(
            [self.instructions, SCHEMA_FOR_CONCEPT_TERMS],
            user_messages
        )
        matches = re.findall(EXTRACT_LIST_REGEX, output, re.DOTALL)
        terms = []
        if matches:
            try:
                # Safely convert the string representation of the list to an actual Python list
                terms = ast.literal_eval(matches[0])
            except (ValueError, SyntaxError):
                terms = []

        if not terms:
            logging.info(f"No terms found in output: {output}")
            return None

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
                    [SELECT_TOPIC_SYSTEM_MESSAGE],
                    [select_topic_prompt(term),
                     string_of_existing_topics_prompt(user_topics)]
                )
                selected_topic = selected_topic_raw.strip("'")

                content = nodeDB().search_for_user_topic_content(selected_topic.strip())
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
            [SUMMARISE_WHILE_RETAINING_DETAIL_SYSTEM_MESSAGE],
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
        raise NotImplementedError(NOT_IMPLEMENTED_IN_INTERFACE)


if __name__ == '__main__':
    pass
