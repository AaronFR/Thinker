import logging
import os
import re
import shutil

from typing import Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context


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
        self.executor = AiOrchestrator()

    @staticmethod
    def categorise_prompt_input(user_prompt: str, llm_response: str = None, creating: bool = True):
        """
        ToDo: reject categories with a / in them, will confuse routing

        :param user_prompt: the input prompt string
        :param llm_response: The optional llm response for additional context
        :param creating: flag if a node or message is being prompted, if the category is just a suggestion new
         categories should not be created in the database
        :return: The name of the selected category
        """
        categories = nodeDB().list_categories()

        if llm_response:
            categorisation_input = "<user prompt>" + user_prompt + "</user prompt>\n" + \
                                   "<response>" + llm_response + "</response>"
            categorisation_instructions = f"LIGHTLY suggested existing categories, you DONT need to follow: {str(categories)}" + \
                "Given the following prompt-response pair, think through step by step, explaining your reasoning" + \
                "and categorize the data with the most suitable single-word answer." + \
                "Write it as <result=\"(your_selection)\""
        else:
            categorisation_input = "<user prompt>" + user_prompt + "</user prompt>\n"
            categorisation_instructions = f"LIGHTLY suggested existing categories, you DONT need to follow: {str(categories)}" + \
                "Given the following prompt, think through step by step, explaining your reasoning" + \
                "and categorize the data with the most suitable single-word answer." + \
                "Write it as <result=\"(your_selection)\""

        category_reasoning = CategoryManagement().executor.execute(
            [categorisation_instructions],
            [categorisation_input]
        )
        logging.info(f"Category Reasoning: {category_reasoning}")
        category = CategoryManagement.extract_example_text(category_reasoning)

        return CategoryManagement.possibly_create_category(category)

    @staticmethod
    def possibly_create_category(category):
        """
        If it doesn't already exist in the node database

        :param category: The category to possibly be added to the node database
        :return: Category
        """
        categories = nodeDB().list_categories()
        if (category not in categories):
            nodeDB().create_category(category)

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

        logging.warning("Failure to categorise!")
        return None

    @staticmethod
    def stage_files(category: str = None):
        """
        Stages files into a specific category based on user prompt.

        This method retrieves files from the staging area, summarises them, and categorises them
        according to their content with the help of an AI orchestrator.

        :param category: If defined the system will categorise the staged files with the given category, otherwise a category will be generated
        """
        files = StorageMethodology.select().list_staged_files()
        logging.info(f"Staged files: {files}")

        category_id = CategoryManagement._return_id_for_category(category)
        logging.info(f"Category selected: [{category_id}] - {category}")

        if not files:
            return

        try:
            user_id = get_user_context()

            for file in files:
                staged_file_path = os.path.join(FileManagement.file_data_directory, user_id, file)
                new_file_path = os.path.join(FileManagement.file_data_directory, str(category_id), file)
                shutil.move(staged_file_path, new_file_path)
                logging.info(f"{file} moved to {category_id}")
        except Exception:
            logging.exception(f"ERROR: Failed to move all files: {files} to folder: {category_id} .")

    @staticmethod
    def _return_id_for_category(category_name: str) -> Optional[str]:
        """Retrieves the ID for the specified category, creating a new category if necessary.

        :param category_name: The name of the category associated with an existing category ID.
        :return: The category ID if found, otherwise None.
        """
        category_id = nodeDB().get_category_id(category_name)
        CategoryManagement._add_new_category(category_id)

        logging.info(f"Id found for category [{category_id}] - {category_name}")

        return category_id

    @staticmethod
    def _add_new_category(category_id: str) -> None:
        """
        Creates the folder to store files against a given category

        :param category_id: The new folder category id to create
        """
        new_directory = os.path.join(FileManagement.file_data_directory, category_id)
        os.makedirs(new_directory, exist_ok=True)  # Create new folder for the given id

    @staticmethod
    def determine_category(user_prompt, tag_category=None):
        """
        Determine the category for the user prompt.

        :param user_prompt: The user's input prompt.
        :param tag_category: The optional tag_category from the front end
        :return: The determined category.
        """
        if not tag_category:
            category = CategoryManagement.categorise_prompt_input(user_prompt)
            logging.info(f"Prompt categorised: {category}")
            return category

        return tag_category


if __name__ == '__main__':
    CategoryManagement.stage_files("Put this file in Notes please")
