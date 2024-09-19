
import logging
import os
import shutil
from typing import List, Dict

import pandas as pd

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.FileManagement import FileManagement
from Functionality.Organising import Organising
from Utilities import Constants, Globals


class CategoryManagement:
    """Manages encyclopedia data files and provides search and retrieval capabilities.

        This class facilitates loading encyclopedia entries and redirects, searching for terms,
        and summarizing information relevant to user queries.
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
        """Initializes the EncyclopediaManagementInterface.
        """
        self.categories: Dict[int, str] = {}

        self.thoughts_directory = os.path.join(os.path.dirname(__file__), '..', 'thoughts')
        self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')
        self.categories_path = os.path.join(self.data_path, "Categories.csv")

        self.load_categories()

    def load_categories(self) -> None:
        """
        Load category data
        """
        try:
            categories_df = pd.read_csv(self.categories_path, names=['id', 'category'], skiprows=1)
            self.categories = categories_df.set_index('id')['category'].to_dict()

            logging.info(f"Categories successfully loaded: \n {self.categories}")
        except FileNotFoundError:
            logging.error("File not found: %s", self.categories_path)
            print("Could not load folder categories data. Ensure the files exist in the specified path.")
        except pd.errors.EmptyDataError:
            logging.error("CSV file is empty: %s", self.categories_path)
            print("The folder categories file is empty, please check the content.")
        except Exception as e:
            logging.exception("Error loading encyclopedia data: %s", exc_info=e)
            print("An unknown error occurred while loading folder categories data. Check logs for more details.")

    def stage_files(self, user_prompt: str):
        """
        Stage files to a given categorical folder
        """
        Globals.current_thought_id = 0  # staging area is 0 in 1-indexed thoughts folder structure
        files = FileManagement.list_file_names()

        # get summaries for executor
        summaries = []
        if files:
            Organising.summarise_files(files)
            files_with_summaries = Organising.get_files_with_summary()

            for file_tuple in files_with_summaries:
                file_name, summary_file_name = file_tuple
                summaries.append(summary_file_name)

        existing_categories = f"The following categories already exist: {self.categories.values()}"
        executor = AiOrchestrator(summaries)
        categorisations = executor.execute_function(
            ["Review the entered files and prompts and determine the category that fits these tasks best",
             existing_categories],
            [user_prompt],
            Constants.DETERMINE_CATEGORY_FUNCTION_SCHEMA
        )['categorisations']
        logging.info(f"Suggested categorisations: {categorisations}")

        if len(categorisations) > 1:
            # ToDO: Split multiple categorisations, for each check if the given category or something similar already
            #  exists then either move the material to that category or create a new one

            logging.warning("'Men at work' 👷‍♂️⚠")
            pass
        else:
            category_name = categorisations[0]['category']
            id = self._return_id_for_category(category_name, executor)
            logging.info(f"Category selected: [{id}] - {category_name}")
            Globals.current_thought_id = id

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

    def _return_id_for_category(self, category_name: str, executor: AiOrchestrator) -> str | None:
        reversed_categories = {v: k for k, v in self.categories.items()}
        id = reversed_categories.get(category_name, False)

        if not id:
            possible_category = executor.execute(
                ["Given the input file and the previous list of categories to id number, is the given input synonym for"
                 " any other category? "
                 "Just return the name of the category, if nothing is similar please just respond with 'False'."
                 "Please be very harsh in your evaluation, only return a possible category if it really SHOULD have"
                 "Been assigned this category but wasn't, it need to be the same categorically, not just *similar*",
                 f"category id with category csv: \n{self.categories}"],
                [category_name]
            )
            logging.info("Possible category: " + possible_category)

            if possible_category != "False":
                id = reversed_categories.get(possible_category)
            else:
                id = FileManagement.get_current_thought_id()
                new_directory = os.path.join(FileManagement.thoughts_directory, str(id))

                os.makedirs(new_directory, exist_ok=True)  # Create new folder for the given id
                self._add_new_category(id, category_name)

                logging.info(f"New category created: [{id}] - {category_name}")

        return id

    @staticmethod
    def _add_new_category(id: int, category_name: str) -> None:
        """
        Fetches the redirects for a given page and appends them to a specified CSV file.

        :param id: The new folder id to create
        :param category_name: The name of this folder in the categorisation system, will be automatically lowercase-d
        """
        category_name = category_name.lower()
        redirect_dicts = [{'id': id, 'category': category_name}]

        fieldnames = ['id', 'category']
        FileManagement.write_to_csv("Categories.csv", redirect_dicts, fieldnames)


if __name__ == '__main__':
    category_management = CategoryManagement()
    category_management.stage_files("Put this file in Notes please")
