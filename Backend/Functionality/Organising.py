import logging
import os

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Data.Files.StorageMethodology import StorageMethodology
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.UserContextManagement import UserContextManagement
from Constants.Instructions import SUMMARISER_SYSTEM_INSTRUCTIONS
from Utilities.Decorators import handle_errors
from Utilities.Utility import Utility


class Organising:

    @staticmethod
    def process_files(files):
        file_references = []
        if files:
            for file in files:
                file_data = nodeDB().get_file_by_id(file.get("id"))
                if not file_data:
                    continue
                file_system_address = f"{file_data['category_id']}\\{file_data['name']}"
                file_references.append(file_system_address)
        return file_references

    @staticmethod
    def save_file(content: str, category_id: str, filename: str, overwrite=True):
        """
        Stores the system in the database, both the content in storage and the file node representation

        :parameter content: As in file content
        :parameter category_id: The id of the category the file will belong to
        :parameter filename: the filename of the file including extension, excluding category folder
        :parameter overwrite: Whether any existing file should be overwritten with this files content
        """
        file_path = os.path.join(category_id, filename)

        file_uuid = nodeDB().create_file_node(category_id, file_path)
        StorageMethodology().select().save_file(content, file_path, overwrite=overwrite)

        return file_uuid

    @staticmethod
    @handle_errors
    def store_prompt_data(
        user_prompt: str,
        response_message: str,
        category: str
    ):
        """
        Populate the initialised message node with the information created by the request workflow

        :param user_prompt: The given user prompt starting the evaluation process
        :param response_message: The systems response
        :param category: The category to register against the prompt node
        :return:
        """
        config = Configuration.load_config()

        Utility.execute_with_retries(
            lambda: nodeDB().populate_user_prompt_node(category, user_prompt, response_message)
        )

        if config['beta_features']['user_context_enabled']:
            terms = UserContextManagement.extract_terms_from_input([user_prompt])
            nodeDB().create_user_topic_nodes(terms)

    @staticmethod
    def summarise_content(content: str):
        """Creates and saves a summary file for the given file.
        ToDo: should use AST for coding files - when we create 'structure' methods

        :param content: The content to be summarised
        """
        summary = AiOrchestrator().execute(
            [SUMMARISER_SYSTEM_INSTRUCTIONS],
            [content]
        )
        return summary


if __name__ == '__main__':
    parent_class_name = "EncyclopediaManagementInterface.py"
    child_class_name = "UserEncyclopediaManagement.py"
    # Organising.get_relevant_files(
    #     "WIP",
    #     [f"Hey can you compare {parent_class_name} and the child class {child_class_name}?"]
    # )
