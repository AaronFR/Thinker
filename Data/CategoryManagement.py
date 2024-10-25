
import logging
import os
import shutil
from typing import Dict, Optional

import pandas as pd

from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement


class CategoryManagement:
    """
    Manages the automatic categorisation of uploaded files by the user and of files created by the system
    """

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    ENCYCLOPEDIA_NAME = "To Define"
    instructions = "To Define"

    _instance = None

    def __new__(cls):
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(CategoryManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the CategoryManagement instance."""
        self.categories: Dict[int, str] = {}  # ToDo NEEDS to be changed, has to grab the users categories

        self.thoughts_directory = os.path.join(os.path.dirname(__file__), '..', 'thoughts')
        self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')
        self.categories_path = os.path.join(self.data_path, "Categories.csv")

        self.load_categories()

    def load_categories(self) -> None:
        """Loads category data from a CSV file into the internal categories' dictionary."""
        try:
            categories_df = pd.read_csv(self.categories_path, names=['id', 'category'], skiprows=1)
            self.categories = categories_df.set_index('id')['category'].to_dict()

            logging.info(f"Categories successfully loaded: \n {self.categories}")
        except FileNotFoundError:
            logging.error("File not found: %s", self.categories_path)
        except pd.errors.EmptyDataError:
            logging.error("CSV file is empty: %s", self.categories_path)
        except Exception as e:
            logging.exception("Error loading encyclopedia data: %s", exc_info=e)

    def stage_files(self, user_prompt: str, category=None):
        """
        Stages files into a specific category based on user prompt.

        This method retrieves files from the staging area, summarises them, and categorises them
        according to their content with the help of an AI orchestrator.

        :param user_prompt: The user-provided prompt to assist with categorisation.
        :param category: If defined the system will categorise the staged files with the given category, otherwise a category will be generated
        """
        files = FileManagement.list_staged_files()

        id = self._return_id_for_category(category)
        logging.info(f"Category selected: [{id}] - {category}")

        if not files:
            return

        try:
            for file in files:
                staged_file_path = os.path.join(FileManagement.thoughts_directory, "0", file)
                new_file_path = os.path.join(FileManagement.thoughts_directory, str(id), file)
                shutil.move(staged_file_path, new_file_path)
                logging.info(f"{file} moved to {id}")
        except Exception:
            logging.exception(f"ERROR: Failed to move all files: {files} to folder: {id} .")


    def _return_id_for_category(self, category_name: str) -> Optional[str]:
        """Retrieves the ID for the specified category, creating a new category if necessary.

        :param category_name: The name of the category associated with an existing category ID.
        :return: The category ID if found, otherwise None.
        """
        reversed_categories = {v: k for k, v in self.categories.items()}
        id = reversed_categories.get(category_name, False)

        if not id:
            node_db = NodeDatabaseManagement()
            id = node_db.get_category_id(category_name)
            self._add_new_category(id, category_name)

            logging.info(f"Id found for category [{id}] - {category_name}")

        return id

    @staticmethod
    def _add_new_category(id: int, category_name: str) -> None:
        """
        Fetches the redirects for a given page and appends them to a specified CSV file.

        :param id: The new folder id to create
        :param category_name: The name of this folder in the categorisation system, will be automatically lowercase-d
        """
        new_directory = os.path.join(FileManagement.thoughts_directory, str(id))
        os.makedirs(new_directory, exist_ok=True)  # Create new folder for the given id

        category_name = category_name.lower()
        redirect_dicts = [{'id': id, 'category': category_name}]

        fieldnames = ['id', 'category']
        FileManagement.write_to_csv("Categories.csv", redirect_dicts, fieldnames)


if __name__ == '__main__':
    category_management = CategoryManagement()
    category_management.stage_files("Put this file in Notes please")
