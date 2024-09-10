import logging
import os
from typing import List, Dict

import pandas as pd
import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.WikipediaApi import wikipedia_page_to_yaml
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING


class EncyclopediaManagement:

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    DEFAULT_ENCYCLOPEDIA_NAME = "Encyclopedia"

    instructions = (
        "For the given prompt return an array of concepts to be searched for in an encyclopedia, "
        "the term should be as simple as possible, e.g., the actual word of the concept. You can use "
        "the 'specifics' field if there is a specific aspect of this concept you would prefer to know more about."
    )
    user_instructions = (
        "For the given prompt return an array of things you want to know about the user, "
        "the term should be as simple as possible, e.g., the actual word of that concept. "
        "You can use the 'specifics' field if there is a specific aspect of this concept you would prefer to know more about."
    )
    # ToDo: Currently the specifics field isn't used at all, but the encyclopedias are then slim and not deep
    #  so currently there is no need

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.encyclopedia: Dict[str, str] = {}
        self.redirects: Dict[str, str] = {}
        self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')

    def search_encyclopedia(self, user_messages: List[str], encyclopedia_name: str = DEFAULT_ENCYCLOPEDIA_NAME) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: The user input messages containing the terms.
        :param encyclopedia_name: The name of the encyclopedia file to use.

        :return: A string representation of the additional context found.
        """
        executor = AiOrchestrator()
        if encyclopedia_name == EncyclopediaManagement.DEFAULT_ENCYCLOPEDIA_NAME:
            instructions = EncyclopediaManagement.instructions
        elif encyclopedia_name == "UserEncyclopedia":
            instructions = EncyclopediaManagement.user_instructions
        else:
            logging.error(f"Invalid encyclopedia: {encyclopedia_name}")
            return None

        output = executor.execute_function(
            [instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"terms to search for in {encyclopedia_name}: {terms}")

        return self.extract_terms_from_encyclopedia(terms, encyclopedia_name)

    def extract_terms_from_encyclopedia(self, terms: List[dict[str, str]], encyclopedia_name: str) -> str:
        """Extract terms from the encyclopedia or fetch them if not found.

        :param terms: The terms to check in the encyclopedia.
        :param encyclopedia_name: The name of the encyclopedia being searched.
        :return: A string representation of additional context extracted.
        """
        self.load_encyclopedia(encyclopedia_name)

        additional_context = []
        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                redirected_term = self.redirects.get(term_name, None)
                if redirected_term:
                    term_name = redirected_term

                entry = self.encyclopedia.get(term_name)
                if entry:
                    additional_context.append((term, entry))
                else:
                    if self.fetch_term_and_update(term_name, encyclopedia_name):
                        entry = self.encyclopedia.get(term_name)
                        if entry:
                            additional_context.append((term, entry))
                    else:
                        logging.error(f"Could not find or create term '{term_name}' after fetching from Wikipedia.")
            except Exception as e:
                logging.exception(f"Error while trying to access {encyclopedia_name}: {term_name}", e)

        return str(additional_context)

    def load_encyclopedia(self, encyclopedia_name: str) -> None:
        """Loads the encyclopedia and redirects if not already loaded.
        ToDo: Create methods for creating encyclopedia and redirect files from scratch if someone happened to fork this project

        :param encyclopedia_name: The name of the encyclopedia to load.
        """
        if not self.encyclopedia:
            encyclopedia_path = os.path.join(self.data_path, encyclopedia_name + self.ENCYCLOPEDIA_EXT)
            if os.path.exists(encyclopedia_path):
                with open(encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                    self.encyclopedia = yaml.safe_load(file) or {}

        if not self.redirects:
            redirect_encyclopedia_path = os.path.join(self.data_path, encyclopedia_name + self.REDIRECTS_EXT)
            if os.path.exists(redirect_encyclopedia_path):
                redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['redirect_term', 'target_term'])
                self.redirects = redirects_df.set_index('redirect_term')['target_term'].to_dict()

    def fetch_term_and_update(self, term_name: str, encyclopedia_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        :param term_name: The name of the term to fetch from Wikipedia.
        :param encyclopedia_name: The name of the encyclopedia to update.
        :return: A status indicating whether the fetching and updating were successful.
        """
        try:
            encyclopedia_path = os.path.join(self.data_path, encyclopedia_name + ".yaml")

            if encyclopedia_name == EncyclopediaManagement.DEFAULT_ENCYCLOPEDIA_NAME:
                wikipedia_page_to_yaml(term_name, encyclopedia_name)
            # don't search wikipedia for the userEncyclopedia
            with open(encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                self.encyclopedia = yaml.safe_load(file)

            redirect_encyclopedia_path = os.path.join(self.data_path, encyclopedia_name + "Redirects.csv")
            redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['redirect_term', 'target_term'])
            self.redirects = redirects_df.set_index('redirect_term')['target_term'].to_dict()

            return True
        except Exception as e:
            logging.exception(f"Error while trying to access '{encyclopedia_name}': '{term_name}'", exc_info=e)
            return False


if __name__ == '__main__':
    """Suggestions
    - Define Xiblic
    """

    encyclopediaManagement = EncyclopediaManagement()
    print(encyclopediaManagement.search_encyclopedia(["Whats my name?"], "UserEncyclopedia"))
    # print(knowing.search_user_encyclopedia(["Do you know what my name is?"]))
