import logging
import os
from typing import List

import pandas as pd
import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface
from Data.FileManagement import FileManagement
from Personas.PersonaSpecification.PersonaConstants import ADD_TO_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING


class UserEncyclopediaManagement(EncyclopediaManagementInterface):

    ENCYCLOPEDIA_NAME = "UserEncyclopedia"

    instructions = (
        "For the given prompt return an array of things you want to know about the user, "
        "the term should be as simple as possible, e.g., the actual word of that concept. "
        "You can use the 'specifics' field if there is a specific aspect of this concept "
        "you would prefer to know more about."
    )
    # ToDo: Currently the specifics field isn't used at all, but the encyclopedias are then slim and not deep
    #  so currently there is no need

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserEncyclopediaManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + ".yaml")
        self.redirect_encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + "Redirects.csv")

    def fetch_term_and_update(self, term_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        :param term_name: The name of the term to fetch from Wikipedia.
        :return: A status indicating whether the fetching and updating were successful.
        """
        try:
            with open(self.encyclopedia_path, 'r', encoding=DEFAULT_ENCODING) as file:
                self.encyclopedia = yaml.safe_load(file)

            redirects_df = pd.read_csv(
                self.redirect_encyclopedia_path,
                header=None,
                names=['redirect_term', 'target_term']
            )
            self.redirects = redirects_df.set_index('redirect_term')['target_term'].to_dict()

            return True
        except Exception as e:
            logging.exception(f"Error while trying to access '{self.ENCYCLOPEDIA_NAME}': '{term_name}'", exc_info=e)
            return False

    def add_to_encyclopedia(self, user_input: List[str]):
        """Review the input user_messages and determine if anything meaningful can be added to the user encyclopedia

        :param user_input: The user input to analyse
        :return: A string representation of the additional context found.
        """
        executor = AiOrchestrator()
        instructions = self.instructions

        terms = executor.execute_function(
            [instructions],
            user_input,
            ADD_TO_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )['terms']
        logging.info(f"terms to search for in {self.ENCYCLOPEDIA_NAME}: {terms}")

        data_path = os.path.join(os.path.dirname(__file__), 'DataStores')
        yaml_filename = self.ENCYCLOPEDIA_NAME + ".yaml"
        yaml_path = os.path.join(data_path, yaml_filename)

        existing_data = FileManagement.load_existing_yaml(yaml_path)
        new_values = {}

        for new_dict in terms:
            try:
                key = new_dict['term']
                value = new_dict['content']
                if key in existing_data:
                    logging.info(f"Key: [{key}] already present in {self.ENCYCLOPEDIA_NAME}.\n"
                                 f"Original: {existing_data.get(key)},\nReplacement: {value}")
                    continue  # Skip if the key exists
                logging.info(f"Adding to {self.ENCYCLOPEDIA_NAME} - {key}: {value}")
                new_values.update({key: value})
            except Exception as e:
                logging.exception(f"Failure to add to {self.ENCYCLOPEDIA_NAME}, for {new_dict}", exc_info=e)

        if new_values:
            FileManagement.write_to_yaml(new_values, yaml_path)


if __name__ == '__main__':
    encyclopediaManagement = UserEncyclopediaManagement()
    # print(encyclopediaManagement.search_encyclopedia(["Do you know what my name is?"]))
    encyclopediaManagement.add_to_encyclopedia(
        [
            "Hey my name is Joe, I work as a Backend Software Developer and I'm coding up a ChatGpt Wrapper hobby "
            "project called 'The Thinker'"
        ]
    )
