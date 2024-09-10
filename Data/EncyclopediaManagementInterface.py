import logging
import os
from typing import List, Dict

import pandas as pd
import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.WikipediaApi import wikipedia_page_to_yaml
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING


class EncyclopediaManagementInterface:

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    ENCYCLOPEDIA_NAME = "ToDefine"

    instructions = ("To Define")
    # ToDo: Currently the specifics field isn't used at all, but the encyclopedias are then slim and not deep
    #  so currently there is no need

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagementInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.encyclopedia: Dict[str, str] = {}
        self.redirects: Dict[str, str] = {}
        self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')

    def search_encyclopedia(self, user_messages: List[str]) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: The user input messages containing the terms.
        :return: A string representation of the additional context found.
        """
        executor = AiOrchestrator()
        instructions = self.instructions

        terms = executor.execute_function(
            [instructions],
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
        self.load_encyclopedia()

        additional_context = []
        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                redirected_term = self.redirects.get(term_name, None)
                if redirected_term:
                    term_name = redirected_term

                entry = self.encyclopedia.get(term_name)
                if entry:
                    entry = self.selectively_process_entry(term_name, term.get('specifics', "Nothing specific"))
                    additional_context.append((term, entry))
                else:
                    if self.fetch_term_and_update(term_name):
                        entry = self.selectively_process_entry(term_name, term.get('specifics', "Nothing specific"))
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

        ToDo: processing an entire wikipedia page (multiple) per prompt is not efficient
        :param term_name: term to search for in encyclopedia data files
        :param specifics: the reason you are searching for this term, what the llm hopes to find more info on
        :return: A shorter processed version of the encyclopedia file
        """
        entry_dict = self.encyclopedia.get(term_name)
        executor = AiOrchestrator()
        output = executor.execute(
            [
                "First I'm going to give you the file for a given term, can you take the extra definition I give you "
                "and reprocess the entry in as few words while retaining as much deep, technical, enriching "
                "information as possible"
            ],
            [
                term_name + ": " + specifics,
                str(entry_dict)
            ]
        )

        return output

    def load_encyclopedia(self) -> None:
        """Loads the encyclopedia and redirects if not already loaded.
        ToDo: Create methods for creating encyclopedia and redirect files from scratch if someone happened to fork this project
        """
        if not self.encyclopedia:
            encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + self.ENCYCLOPEDIA_EXT)
            if os.path.exists(encyclopedia_path):
                with open(encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                    self.encyclopedia = yaml.safe_load(file) or {}

        if not self.redirects:
            redirect_encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + self.REDIRECTS_EXT)
            if os.path.exists(redirect_encyclopedia_path):
                redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['redirect_term', 'target_term'])
                self.redirects = redirects_df.set_index('redirect_term')['target_term'].to_dict()

    def fetch_term_and_update(self, term_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        :param term_name: The name of the term to fetch from Wikipedia.
        :return: A status indicating whether the fetching and updating were successful.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


if __name__ == '__main__':
    pass
