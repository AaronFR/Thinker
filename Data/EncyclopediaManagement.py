import logging
import os
from typing import List

import pandas as pd
import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING


class EncyclopediaManagement:

    data_path = os.path.join(os.path.dirname(__file__), 'DataStores')
    instructions = "For the given prompt return an array of concepts to be searched for in an encyclopedia, the term"
    "should be as simple as possible, e.g. the actual word of the concept. You can use the 'specifics' field if there"
    "is a specific aspect of this concept you would prefer to know more about in particular"
    user_instructions = "For the given prompt return an array of things you want to know about the user, the term"
    "should be as simple as possible, e.g. the actual word of that concept. You can use the 'specifics' field if there"
    "is a specific aspect of this concept you would prefer to know more about in particular"
    # ToDo: Currently the specifics field isn't used at all, but the encyclopedias are then slim and not deep
    #  so currently there is no need

        executor = AiOrchestrator()
        output = executor.execute_function(
            [EncyclopediaManagement.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"terms to search for in encyclopedia: {terms}")
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.encyclopedia = {}
        self.redirects = {}

    def search_encyclopedia(self, user_messages: List[str], encyclopedia_name: str = "Encyclopedia"):
        executor = AiOrchestrator()
        output = executor.execute_function(
            [EncyclopediaManagement.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"terms to search for in user encyclopedia: {terms}")

        encyclopedia_path = os.path.join(EncyclopediaManagement.data_path, "UserEncyclopedia.yaml")
        redirect_encyclopedia_path = os.path.join(EncyclopediaManagement.data_path,
                                                  "UserEncyclopediaRedirects.csv")
        with open(encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
            encyclopedia = yaml.safe_load(file)

        redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['term', 'redirect'])
        redirects = pd.Series(redirects_df.redirect.values, index=redirects_df.term).to_dict()

        return self.extract_terms_from_encyclopedia(terms, encyclopedia_name)

    @staticmethod
    def extract_terms_from_encyclopedia(terms, encyclopedia: str) -> str:
        encyclopedia_path = os.path.join(EncyclopediaManagement.data_path, encyclopedia + ".yaml")
        redirect_encyclopedia_path = os.path.join(EncyclopediaManagement.data_path, encyclopedia + "Redirects.csv")

        if not self.encyclopedia:
            with open(encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                self.encyclopedia = yaml.safe_load(file)
        if not self.redirects:
            #ToDo: Create methods for creating encycolopedia and redirect files from scratch if someone happened to fork this project
            redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['redirect_term', 'target_term'])
            self.redirects = pd.Series(redirects_df.redirect_term.values, index=redirects_df.target_term).to_dict()

        additional_context = ()
        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                redirected_term = self.redirects.get(term_name, None)
                if redirected_term:
                    term_name = redirected_term

                if self.encyclopedia.get(term_name, False):
                    additional_context += (term, self.encyclopedia[term_name])
                else:
                    wikipedia_page_to_yaml(term_name, encyclopedia_name)
                    with open(encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                        self.encyclopedia = yaml.safe_load(file)
                    additional_context += (term, self.encyclopedia.get(term_name))
            except Exception as e:
                logging.exception(f"Error while trying to access {encyclopedia_name}: {term_name}", e)

        return str(additional_context)


if __name__ == '__main__':
    """Suggestions
    - Define Xiblic
    """

    encyclopediaManagement = EncyclopediaManagement()
    print(encyclopediaManagement.search_encyclopedia(["Define Xiblic?"]))
    # print(knowing.search_user_encyclopedia(["Do you know what my name is?"]))
