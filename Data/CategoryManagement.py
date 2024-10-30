
import logging
import os
import re
import shutil
from typing import Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement


class CategoryManagement:
    """
    Manages the automatic categorisation of uploaded files by the user and of files created by the system
    """

    _instance = None

    def __new__(cls):
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(CategoryManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.node_db = NodeDatabaseManagement()
        self.executor = AiOrchestrator()

    def categorise_prompt_input(self, user_prompt: str, llm_response: str):
        categories = self.node_db.list_categories()
        categorisation_input = "<user prompt>" + user_prompt + "</user prompt>\n" + \
                               "<response>" + llm_response + "</response>"

        category_reasoning = self.executor.execute(
            [
                f"LIGHTLY suggested existing categories, you DONT need to follow: {str(categories)}"
                "Given the following prompt-response pair, think through step by step, explaining your reasoning"
                "and categorize the data with the most suitable single-word answer."
                "Write it as <result=\"(your_selection)\""
            ],
            [categorisation_input]
        )
        logging.info(f"Category Reasoning: {category_reasoning}")
        category = CategoryManagement.extract_example_text(category_reasoning)

        if category not in categories:
            self.node_db.create_category(category)

        return category

    @staticmethod
    def extract_example_text(input_string):
        """
        Extracts the text contained within the result element.

        :param input_string: The string containing the result element.
        :type input_string: str
        :return: The text inside the result element or None if not found.
        :rtype: str or None
        """
        match = re.search(r'<result="([^"]+)">', input_string)
        if match:
            return match.group(1)
        return None

    def stage_files(self, user_id: str, category=None):
        """
        Stages files into a specific category based on user prompt.

        This method retrieves files from the staging area, summarises them, and categorises them
        according to their content with the help of an AI orchestrator.

        :param user_id: The user-provided id
        :param category: If defined the system will categorise the staged files with the given category, otherwise a category will be generated
        """
        files = FileManagement.list_staged_files(user_id)
        logging.info(f"Staged files: {files}")

        id = self._return_id_for_category(category)
        logging.info(f"Category selected: [{id}] - {category}")

        if not files:
            return

        try:
            for file in files:
                staged_file_path = os.path.join(FileManagement.file_data_directory, user_id, file)
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
        id = self.node_db.get_category_id(category_name)
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
