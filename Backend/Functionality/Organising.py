import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.CategoryManagement import CategoryManagement
from Data.Configuration import Configuration
from Data.Files.StorageMethodology import StorageMethodology
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.UserContextManagement import UserContextManagement
from Utilities.Contexts import set_functionality_context
from Constants.Instructions import SUMMARISER_SYSTEM_INSTRUCTIONS
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
    def save_file(content: str, category: str, file_path: str, overwrite=True):
        """
        Stores the system in the database, both the content in storage and the file node representation

        :parameter content: As in file content
        :parameter category: With respect to files the folder files are stored in
        :parameter file_path: the full file address including folder directory and file name with extension.
        """
        nodeDB().create_file_node(category, file_path)
        StorageMethodology().select().save_file(content, file_path, overwrite=overwrite)

    @staticmethod
    def store_prompt_data(
        user_prompt: str,
        response_message: str,
        category: str
    ):
        """
        ToDo: Look into celery and async processing

        :param user_prompt: The given user prompt starting the evaluation process
        :param response_message: The systems response
        :param category: The category to register against the prompt node
        :return:
        """
        config = Configuration.load_config()
        set_functionality_context(None)  # ToDo: Really different contexts should be isolated by thread.

        Utility.execute_with_retries(
            lambda: nodeDB().populate_user_prompt_node(category, user_prompt, response_message)
        )

        if config['beta_features']['user_context_enabled']:
            terms = UserContextManagement.extract_terms_from_input([user_prompt])
            nodeDB().create_user_topic_nodes(terms)

        CategoryManagement.stage_files(category)

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
    child_class_name = "UserEncyclopediaMangement.py"
    # Organising.get_relevant_files(
    #     "WIP",
    #     [f"Hey can you compare {parent_class_name} and the child class {child_class_name}?"]
    # )
