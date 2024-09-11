import logging
import os

import pandas as pd
import yaml

from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface
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


if __name__ == '__main__':
    encyclopediaManagement = UserEncyclopediaManagement()
    print(encyclopediaManagement.search_encyclopedia(["Whats my name?"]))
    # print(knowing.search_user_encyclopedia(["Do you know what my name is?"]))
