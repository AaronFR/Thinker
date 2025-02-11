import logging
import os
import re
from typing import Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Constants import RESULT_AS_TAG_REGEX, SENTENCE_WITH_FULL_STOP_REGEX
from Constants.Exceptions import failure_to_suggest_colour_for_category, failure_to_create_description_for_category
from Data.Configuration import Configuration
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Utilities import Colour
from Constants.Instructions import DEFAULT_USER_CATEGORISATION_INSTRUCTIONS, categorisation_system_message, \
    categorisation_prompt, SELECT_COLOUR_SYSTEM_MESSAGE, CATEGORY_DESCRIPTION_SYSTEM_MESSAGE, \
    category_description_prompt


class CategoryManagement:
    """
    Manages the automatic categorisation of uploaded files and files created by the system.
    """

    _instance = None
    CATEGORIZATION_TEMPLATE = """<user prompt>{}</user prompt>
    <response>{}</response>"""

    def __new__(cls):
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(CategoryManagement, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def sanitise_category_name(category: str) -> str:
        """
        Sanitize the category name to remove invalid characters like '/'.


        :param category: The category name to be sanitized.
        :return: A sanitized category name.
        """
        return category.replace('/', '_')  # Replace '/' to avoid routing issues

    @staticmethod
    def categorise_prompt_input(user_prompt: str, llm_response: Optional[str] = None) -> str | None:
        """
        Categorizes the user input based on prompt and optional response using the AI orchestrator.

        :param user_prompt: The user's input prompt string.
        :param llm_response: The optional llm response for additional context
        :return: Name of the selected category.
        """
        category_names = nodeDB().list_category_names()
        config = Configuration.load_config()

        user_categorisation_instructions = config.get('systemMessages', {}).get(
            "categorisationMessage",
            DEFAULT_USER_CATEGORISATION_INSTRUCTIONS
        )

        category_reasoning = AiOrchestrator().execute(
            [categorisation_prompt(category_names, user_categorisation_instructions)],
            [categorisation_system_message(user_prompt, llm_response)]
        )
        logging.info(f"Category Reasoning: {category_reasoning}")

        category = CategoryManagement.extract_result(category_reasoning)
        if not category:
            logging.warning("Failure to categorize! Invalid category provided.")
            return None

        return CategoryManagement.possibly_create_category(category, category_reasoning)

    @staticmethod
    def possibly_create_category(category: str, additional_context: str = None) -> str:
        """
        Creates a category in the database if it does not already exist.

        :param category: The category to potentially add to the node database.
        :param additional_context: Additional context for determining parameters
        :return: The existing or newly created category.
        """
        sanitized_category = CategoryManagement.sanitise_category_name(category)
        categories = nodeDB().list_category_names()

        if sanitized_category not in categories:
            color = CategoryManagement.generate_colour(sanitized_category)
            description = CategoryManagement.generate_category_description(
                sanitized_category,
                additional_context
            )
            nodeDB().create_category(sanitized_category, description, color)

        return sanitized_category

    @staticmethod
    def extract_result(input_string: str) -> Optional[str]:
        """
        Extracts the text contained within the result element.

        :param input_string: The string containing the result element.
        :return: The text inside the result element or None if not found.
        """
        match = re.search(RESULT_AS_TAG_REGEX, input_string)
        if match:
            return match.group(1)

        logging.warning("Failed to categorize input string.")
        return None

    @staticmethod
    def stage_files(category: Optional[str] = None) -> None:
        """
        Stages files into a specific category based on the user prompt.

        This method retrieves files from the staging area, summarises them, and categorises them
        according to their content with the help of an AI orchestrator.

        :param category: The category for staged files. If None, a category will be generated.
        """
        files = StorageMethodology.select().list_staged_files()
        logging.info(f"Staged files: {files}")

        category_id = CategoryManagement._get_or_create_category_id(category)
        logging.info(f"Category selected: [{category_id}] - {category}")

        if not files:
            return

        for file in files:
            staged_file_path = os.path.join(file)
            new_file_path = os.path.join(str(category_id), os.path.basename(file))

            StorageMethodology.select().move_file(staged_file_path, new_file_path)
        logging.info(f"All files moved to category: {category_id}.")

    @staticmethod
    def _get_or_create_category_id(category_name: str) -> Optional[str]:
        """Retrieves or creates a category ID for the specified category name.

        :param category_name: The name of the category.
        :return: The category ID if found; otherwise None.
        """
        sanitized_category_name = CategoryManagement.sanitise_category_name(category_name)
        category_id = nodeDB().get_category_id(sanitized_category_name)

        StorageMethodology.select().add_new_category_folder(category_id)

        return category_id

    @staticmethod
    def determine_category(user_prompt: str, tag_category: Optional[str] = None) -> str:
        """
        Determine the category for the user prompt.

        :param user_prompt: The user's input prompt.
        :param tag_category: Optional tag category from the front end.
        :return: The determined category.
        """
        if not tag_category:
            category = CategoryManagement.categorise_prompt_input(user_prompt)
            logging.info(f"Prompt categorised: {category}")
            return category

        return tag_category

    @staticmethod
    def is_valid_description(description: str) -> bool:
        """
        Validates the AI-generated description.

        :param description: The description to validate.
        :return: True if valid, False otherwise.
        """
        return bool(re.match(SENTENCE_WITH_FULL_STOP_REGEX, description))

    @staticmethod
    def default_description(category_name: str) -> str:
        """
        Provides a default description for the category if AI fails.

        :param category_name: The name of the category.
        :return: A default description.
        """
        default = f"A category for {category_name.lower()} related items."
        logging.debug(f"Default description for '{category_name}': {default}")
        return default

    @staticmethod
    def generate_colour(category_name: str) -> Optional[str]:
        """
        Generate a meaningful color based on the category name using AI.

        :param category_name: The name of the category.
        :return: A string representing a color in HEX format or None if AI call fails.
        """
        user_prompts = [f"Category Name: {category_name}"]

        config = Configuration.load_config()
        use_ai = config['interface'].get("ai_colour", False)
        try:
            if use_ai:
                ai_response = AiOrchestrator().execute(
                    [SELECT_COLOUR_SYSTEM_MESSAGE],
                    user_prompts
                )
                ai_color = ai_response.strip()
                if Colour.is_valid_hex_color(ai_color):
                    logging.info(f"AI assigned color '{ai_color}' for category '{category_name}'.")
                    return ai_color

            return Colour.generate_random_colour()
        except Exception:
            logging.exception(failure_to_suggest_colour_for_category(category_name))
            return None

    @staticmethod
    def generate_category_description(category_name: str, additional_context: str = "") -> str:
        """
        Generates a short description for the given category name using AI.

        :param category_name: The name of the category to describe.
        :param additional_context: Optionally add the user prompt for additional context
        :return: A short description of the category.
        """
        try:
            description = AiOrchestrator().execute(
                [CATEGORY_DESCRIPTION_SYSTEM_MESSAGE],
                [
                    category_description_prompt(category_name),
                    additional_context,
                ]
            )
            description = description.strip()

            if CategoryManagement.is_valid_description(description):
                logging.debug(f"AI-generated description for '{category_name}': {description}")
                return description
            else:
                logging.warning(
                    f"AI response '{description}' is not a valid description. Using default description."
                )
                return CategoryManagement.default_description(category_name)
        except Exception:
            logging.exception(failure_to_create_description_for_category(category_name))
            return CategoryManagement.default_description(category_name)


if __name__ == '__main__':
    CategoryManagement().stage_files("Put this file in Notes please")
