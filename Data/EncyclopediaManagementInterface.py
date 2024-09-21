import logging
import os
from typing import List, Dict

import pandas as pd
import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING


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

    def __new__(cls):
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagementInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the EncyclopediaManagementInterface.
        """
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.encyclopedia: Dict[str, str] = {}
            self.redirects: Dict[str, str] = {}

            self.encyclopedia_path = "To Define"
            self.redirect_encyclopedia_path = "To Define"

            self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')
            self.initialized = True

    def load_encyclopedia_data(self) -> None:
        """Load encyclopedia and redirect data from the specified files."""
        self.encyclopedia = self._load_yaml_file(self.encyclopedia_path)
        self.redirects = self._load_redirects(self.redirect_encyclopedia_path)

        logging.info("Encyclopedia and redirects loaded successfully")

    @staticmethod
    def _load_yaml_file(filepath: str) -> Dict[str, str]:
        """Load a YAML file and return its content."""
        try:
            with open(filepath, 'r', encoding=DEFAULT_ENCODING) as file:
                return yaml.safe_load(file) or {}

        except yaml.YAMLError as yml_err:
            logging.error("YAML error while loading encyclopedia data: %s", yml_err)
        except Exception as e:
            logging.exception("Error loading encyclopedia data", exc_info=e)

    @staticmethod
    def _load_redirects(filepath: str) -> Dict[str, str]:
        """Load redirect terms from a CSV file and return them as a dictionary."""
        try:
            redirects_df = pd.read_csv(filepath, header=None, names=['redirect_term', 'target_term'])
            return redirects_df.set_index('redirect_term')['target_term'].to_dict()

        except pd.errors.EmptyDataError:
            logging.error("CSV file is empty: %s", filepath)
        except Exception as e:
            logging.exception("Error loading user encyclopedia data: %s", exc_info=e)

    def search_encyclopedia(self, user_messages: List[str]) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: The user input messages containing the terms.
        :return: A string representation of the additional context found.
        """
        executor = AiOrchestrator()

        try:
            output = executor.execute_function(
                [self.instructions],
                user_messages,
                SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
            )
            terms = output['terms']
            logging.info(f"terms to search for in {self.ENCYCLOPEDIA_NAME}: {terms}")

            return self.extract_terms_from_encyclopedia(terms)
        except KeyError:
            logging.error("Output error: expected 'terms' key missing in the response.")
            return "An error occurred while processing the search."
        except Exception:
            logging.error(f"failed to process terms: {output}")
            return "An error occurred while searching the encyclopedia."

    def extract_terms_from_encyclopedia(self, terms: List[dict[str, str]]) -> str:
        """Extract terms from the encyclopedia or fetch them if not found.

        :param terms: The terms to check in the encyclopedia.
        :return: A string representation of additional context extracted.
        """
        additional_context = []

        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                redirected_term = self.redirects.get(term_name)
                if redirected_term:
                    term_name = redirected_term

                entry = self.encyclopedia.get(term_name)
                specifics = term.get('specifics', "Nothing specific")

                if entry:
                    entry = self.selectively_process_entry(term_name, specifics)
                    additional_context.append((term, entry))
                elif self.fetch_term_and_update(term_name):
                    entry = self.selectively_process_entry(term_name, specifics)
                    if entry:
                        additional_context.append((term, entry))
                else:
                    logging.error(f"Could not find or create term '{term_name}' after fetching from Wikipedia.")
            except Exception as e:
                logging.exception(f"Error while trying to access {self.ENCYCLOPEDIA_NAME}: {term_name}", exc_info=e)

        return str(additional_context)

    def selectively_process_entry(self, term_name: str, specifics: str) -> str:
        """Must be run after data files have been loaded.

        :param term_name: term to search for in encyclopedia data files
        :param specifics: the reason you are searching for this term, what the llm hopes to find more info on
        :return: A shorter processed version of the encyclopedia file
        """
        entry_dict = self.encyclopedia.get(term_name)
        executor = AiOrchestrator()
        output = executor.execute(
            [
                "Summarize the following information while retaining essential details."
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
