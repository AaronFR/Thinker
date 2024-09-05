import logging
import os
from typing import List

import pandas as pd
import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA


class Knowing:

    data_path = os.path.join(os.path.dirname(__file__), '..', 'Data')
    instructions = "For the given prompt return an array of concepts to be searched for in an encyclopedia, the term"
    "should be as simple as possible, e.g. the actual word of the concept. You can use the 'specifics' field if there"
    "is a specific aspect of this concept you would prefer to know more about in particular"
    user_instructions = "For the given prompt return an array of things you want to know about the user, the term"
    "should be as simple as possible, e.g. the actual word of that concept. You can use the 'specifics' field if there"
    "is a specific aspect of this concept you would prefer to know more about in particular"
    # ToDo: Currently the specifics field isn't used at all, but the encyclopedias are then slim and not deep
    #  so currently there is no need

    @staticmethod
    def search_encyclopedia(user_messages: List[str]):
        executor = AiOrchestrator()
        output = executor.execute_function(
            [Knowing.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"terms to search for in encyclopedia: {terms}")

        return Knowing.extract_terms_from_encyclopedia(terms, "Encyclopedia")

    @staticmethod
    def search_user_encyclopedia(user_messages: List[str]):
        executor = AiOrchestrator()
        output = executor.execute_function(
            [Knowing.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"terms to search for in user encyclopedia: {terms}")

        encyclopedia_path = os.path.join(Knowing.data_path, "UserEncyclopedia.yaml")
        redirect_encyclopedia_path = os.path.join(Knowing.data_path, "UserEncyclopediaRedirects.csv")
        with open(encyclopedia_path, 'r') as file:
            encyclopedia = yaml.safe_load(file)

        redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['term', 'redirect'])
        redirects = pd.Series(redirects_df.redirect.values, index=redirects_df.term).to_dict()

        return Knowing.extract_terms_from_encyclopedia(terms, "UserEncyclopedia")

    @staticmethod
    def extract_terms_from_encyclopedia(terms, encyclopedia: str) -> str:
        encyclopedia_path = os.path.join(Knowing.data_path, encyclopedia + ".yaml")
        redirect_encyclopedia_path = os.path.join(Knowing.data_path, encyclopedia + "Redirects.csv")

        with open(encyclopedia_path, 'r') as file:
            encyclopedia = yaml.safe_load(file)
        redirects_df = pd.read_csv(redirect_encyclopedia_path, header=None, names=['term', 'redirect'])
        redirects = pd.Series(redirects_df.redirect.values, index=redirects_df.term).to_dict()

        additional_context = ()
        for term in terms:
            term_name = term['term'].lower().strip()
            try:
                redirected_term = redirects.get(term_name, None)
                if redirected_term:
                    term_name = redirected_term
                additional_context += (term, encyclopedia[term_name])
            except Exception:
                logging.warning(f"Term not found in encyclopedia: {term_name}")

        return str(additional_context)


if __name__ == '__main__':
    """Suggestions
    - Define Xiblic
    """

    knowing = Knowing()
    print(knowing.search_encyclopedia(["Define Xiblic?"]))
    # print(knowing.search_user_encyclopedia(["Do you know what my name is?"]))
