import logging
import os

from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface
from Data.WikipediaApi import search_wikipedia_api
from Utilities.Decorators import return_for_error


class EncyclopediaManagement(EncyclopediaManagementInterface):
    """
    **EncyclopediaManagement**: A class for managing encyclopedia entries, enabling retrieval,
    updating, and organization of knowledge.

    This class implements a singleton pattern to ensure a single instance to ensure only a single cache is held in
    memory.
    """

    ENCYCLOPEDIA_NAME = "Encyclopedia"

    instructions = (
        "For the given prompt, return an array of concepts that would help answer this prompt. "
        "The term should be simple, e.g., the actual word of the concept. You can use "
        "the 'specifics' field if there is a particular aspect you would prefer to explore."
    )

    _instance = None

    def __new__(cls) -> "EncyclopediaManagement":
        """Create a singleton instance of EncyclopediaManagement."""
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the EncyclopediaManagement instance, setting paths for the encyclopedia data files
        and loading the initial data.
        """
        super().__init__()
        self.encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + ".yaml")
        self.redirect_encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + "Redirects.csv")
        self.load_encyclopedia_data()

    @return_for_error(False)
    def fetch_term_and_update(self, term_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        This method retrieves the specified term's data from the Wikipedia API and refreshes the local encyclopedia
        cache to reflect the most current information. If any exception occurs during the process, it logs the error.

        :param term_name: The name of the term to fetch from Wikipedia.
        :return: A status indicating whether the fetching and updating were successful.
        """
        search_wikipedia_api(term_name, self.ENCYCLOPEDIA_NAME)
        self.load_encyclopedia_data()

        return True


if __name__ == '__main__':
    encyclopedia_management = EncyclopediaManagement()
    result = encyclopedia_management.search_encyclopedia(["Can you talk about 'code reuse'?"])
    print(result)
