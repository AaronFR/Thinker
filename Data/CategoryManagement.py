
import logging
import os
import shutil
from typing import Optional

from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement


class CategoryManagement:
    """
    Manages the automatic categorisation of uploaded files by the user and of files created by the system
    """

    ENCYCLOPEDIA_EXT = ".yaml"
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
        self.file_data_directory = os.path.join(os.path.dirname(__file__), 'FileData')
        self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')

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
                staged_file_path = os.path.join(FileManagement.file_data_directory, "0", file)
                new_file_path = os.path.join(FileManagement.file_data_directory, str(id), file)
                shutil.move(staged_file_path, new_file_path)
                logging.info(f"{file} moved to {id}")
        except Exception:
            logging.exception(f"ERROR: Failed to move all files: {files} to folder: {id} .")

    def _return_id_for_category(self, category_name: str) -> Optional[str]:
        """Retrieves the ID for the specified category, creating a new category if necessary.

        :param category_name: The name of the category associated with an existing category ID.
        :return: The category ID if found, otherwise None.
        """
        node_db = NodeDatabaseManagement()
        id = node_db.get_category_id(category_name)
        self._add_new_category(id)

        logging.info(f"Id found for category [{id}] - {category_name}")

        return id

    @staticmethod
    def _add_new_category(id: int) -> None:
        """
        Fetches the redirects for a given page and appends them to a specified CSV file.

        :param id: The new folder id to create
        """
        new_directory = os.path.join(FileManagement.file_data_directory, str(id))
        os.makedirs(new_directory, exist_ok=True)  # Create new folder for the given id


if __name__ == '__main__':
    category_management = CategoryManagement()
    category_management.stage_files("Put this file in Notes please")
