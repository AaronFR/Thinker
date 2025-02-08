from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.CategoryManagement import CategoryManagement
from Data.Configuration import Configuration
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.UserContextManagement import UserContextManagement
from Utilities.Contexts import set_functionality_context
from Constants.Instructions import SUMMARISER_SYSTEM_INSTRUCTIONS


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
    def categorize_and_store_prompt(user_prompt: str,
                                    response_message: str,
                                    category: str = None):
        """
        ToDo: Look into celery and async processing

        :param user_prompt: The given user prompt starting the evaluation process
        :param response_message: The systems response
        :param category: The category to register against the prompt node
        :return:
        """
        config = Configuration.load_config()
        set_functionality_context(None)  # ToDo: Really different contexts should be isolated by thread.

        if not category:
            category = CategoryManagement.categorise_prompt_input(user_prompt, response_message)
        else:
            category = CategoryManagement.possibly_create_category(category)
        nodeDB().populate_user_prompt_node(category, user_prompt, response_message)

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
