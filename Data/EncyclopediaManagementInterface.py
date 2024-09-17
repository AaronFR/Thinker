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
        """Initializes the EncyclopediaManagementInterface.

        :param executor: An instance of AiOrchestrator for executing external functions.
                         If none is provided, a new instance will be created.
        """
        self.encyclopedia: Dict[str, str] = {}
        self.redirects: Dict[str, str] = {}

        self.encyclopedia_path = "To Define"
        self.redirect_encyclopedia_path = "To Define"

        self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')

    def load_encyclopedia_data(self) -> None:
        """
        Load encyclopedia and redirect data from the specified files.
        """
        try:
            with open(self.encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                self.encyclopedia = yaml.safe_load(file) or {}

            redirects_df = pd.read_csv(self.redirect_encyclopedia_path, header=None,
                                       names=['redirect_term', 'target_term'])
            self.redirects = redirects_df.set_index('redirect_term')['target_term'].to_dict()

            logging.info("Encyclopedia and redirects loaded successfully")
        except FileNotFoundError:
            logging.error("File not found: %s", self.encyclopedia_path)
            print("Could not load encyclopedia data. Ensure the files exist in the specified path.")
        except yaml.YAMLError as yml_err:
            logging.error("YAML error while loading encyclopedia data: %s", yml_err)
            print("Error loading encyclopedia data format. Please check the file's syntax.")
        except pd.errors.EmptyDataError:
            logging.error("CSV file is empty: %s", self.redirect_encyclopedia_path)
            print("The redirects file is empty, please check the content.")
        except Exception as e:
            logging.exception("Error loading encyclopedia data: %s", exc_info=e)
            print("An unknown error occurred while loading encyclopedia data. Check logs for more details.")

    def search_encyclopedia(self, user_messages: List[str]) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: The user input messages containing the terms.
        :return: A string representation of the additional context found.
        """
        executor = AiOrchestrator()

        terms = executor.execute_function(
            [self.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )['terms']
        logging.info(f"terms to search for in {self.ENCYCLOPEDIA_NAME}: {terms}")

        return self.extract_terms_from_encyclopedia(terms)

    def extract_terms_from_encyclopedia(self, terms: List[dict[str, str]]) -> str:
        """Extract terms from the encyclopedia or fetch them if not found.

        :param terms: The terms to check in the encyclopedia.
        :return: A string representation of additional context extracted.
        """
        additional_context = []

        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                redirected_term = self.redirects.get(term_name, None)
                if redirected_term:
                    term_name = redirected_term

                entry = self.encyclopedia.get(term_name)
                specifics = term.get('specifics', "Nothing specific")
                if entry:
                    entry = self.selectively_process_entry(term_name, specifics)
                    additional_context.append((term, entry))
                else:
                    if self.fetch_term_and_update(term_name):
                        entry = self.selectively_process_entry(term_name, specifics)
                        if entry:
                            additional_context.append((term, entry))
                    else:
                        logging.error(f"Could not find or create term '{term_name}' after fetching from Wikipedia.")
            except Exception as e:
                logging.exception(f"Error while trying to access {self.ENCYCLOPEDIA_NAME}: {term_name}", e)

        return str(additional_context)

    def selectively_process_entry(self, term_name: str, specifics: str):
        """
        Must be run after data files have been loaded.

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
