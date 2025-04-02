import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import shortuuid
from flask import copy_current_request_context

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Constants import RESULT_AS_TAG_REGEX, SENTENCE_WITH_FULL_STOP_REGEX, DEFAULT_CATEGORY
from Constants.Exceptions import failure_to_suggest_colour_for_category, failure_to_create_description_for_category
from Data.Configuration import Configuration
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Utilities import Colour
from Constants.Instructions import DEFAULT_USER_CATEGORISATION_INSTRUCTIONS, categorisation_inputs, \
    SELECT_COLOUR_SYSTEM_MESSAGE, CATEGORY_DESCRIPTION_SYSTEM_MESSAGE, category_description_prompt, \
    categorisation_system_messages
from Utilities.Contexts import set_category_context, get_category_context, set_message_context, set_user_context, \
    set_iteration_context, get_user_context, get_message_context
from Utilities.Decorators.Decorators import specify_functionality_context


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
        Then lowercase the category in line with DB expectations


        :param category: The category name to be sanitized.
        :return: A sanitized category name.
        """
        return category.replace('/', '_').lower()  # Replace '/' to avoid routing issues

    @staticmethod
    @specify_functionality_context("select_category")
    def categorise_input(content: str, llm_response: Optional[str] = None) -> str | None:
        """
        Categorizes the user input based on content and optional response using the AI orchestrator.

        :param content: The content to be categorised
        :param llm_response: The optional llm response for additional context
        :return: Name of the selected category.
        """
        category_names = nodeDB().list_category_names()
        config = Configuration.load_config()

        user_categorisation_instructions = config.get('system_messages', {}).get(
            "categorisation_message",
            DEFAULT_USER_CATEGORISATION_INSTRUCTIONS
        )

        category_reasoning = AiOrchestrator().execute(
            categorisation_system_messages(user_categorisation_instructions),
            categorisation_inputs(content, llm_response, category_names)
        )
        logging.info(f"Category Reasoning: {category_reasoning}")

        category = CategoryManagement.extract_result(category_reasoning)
        if not category:
            logging.warning("Failure to categorize! Invalid category provided. Setting to 'default'")
            return DEFAULT_CATEGORY

        return CategoryManagement.sanitise_category_name(category)

    # Define category context

    @staticmethod
    def create_initial_user_prompt_and_possibly_new_category(category: str, user_prompt: str):
        """
        Defines a blank user_prompt to be populated later at the end of the request, using the original user_prompt as
        extra contextual information for defining the category_node at the same time.

        We define both simultaneously to avoid any race conditions where a newly created category is created but not made
        available in time for a subsequent request within the prompt

        :param category: The category name that has been decided upon
        :param user_prompt: used as context for deciding the category's description
        :return:
        """
        categories = nodeDB().list_category_names()

        if category not in categories:
            category_id, description, color = CategoryManagement.define_new_category(category, user_prompt)
            nodeDB().create_category_and_user_prompt(category_id, category, description, color)
        else:
            category_id = nodeDB().get_category_id(category)
            nodeDB().create_user_prompt_node(category)

        set_category_context(category_id)

    @staticmethod
    def possibly_create_new_category(category: str):
        categories = nodeDB().list_category_names()

        if category not in categories:
            category_id, description, color = CategoryManagement.define_new_category(category)
            nodeDB().create_category(category_id, category, description, color)
        else:
            category_id = nodeDB().get_category_id(category)

        set_category_context(category_id)

    @staticmethod
    def define_new_category(category: str, additional_context: str = ""):
        """
        Defines a new category, generating its color and description concurrently.

        :param category: The category name
        :param additional_context: The user's prompt which is used as context when creating descriptions
        :return: The id, description and color of the new category
        :raises Exception: Propagates exceptions from underlying generation functions.
        """
        category_id = str(shortuuid.uuid())
        user_id = get_user_context()
        message_id = get_message_context()
        set_category_context(category_id)

        def wrapped_process_generate_colour(category, user_id, category_id, message_id):
            set_user_context(user_id)
            set_category_context(category_id)
            set_message_context(message_id)

            return CategoryManagement.generate_colour(category)

        def wrapped_process_generate_category_description(category, additional_context, user_id, category_id, message_id):
            set_user_context(user_id)
            set_category_context(category_id)
            set_message_context(message_id)

            return CategoryManagement.generate_category_description(
                category_name=category,
                additional_context=additional_context
            )

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix='CategoryGen') as executor:
            color_future = executor.submit(
                copy_current_request_context(wrapped_process_generate_colour),
                category,
                user_id,
                category_id,
                message_id
            )
            description_future = executor.submit(
                copy_current_request_context(wrapped_process_generate_category_description),
                category,
                additional_context,
                user_id,
                category_id,
                message_id
            )

            logging.info(f"Tasks submitted for '{category}'. Waiting for results...")
            try:
                description_result = description_future.result()
                logging.info(f"Description result received for '{category}'.")
                color_result = color_future.result()
                logging.info(f"Color result received for '{category}'.")

            except Exception as e:
                logging.error(f"Error during concurrent category generation for '{category}': {e}", exc_info=True)
                raise

        return category_id, description_result, color_result

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
    def _get_or_create_category_id() -> Optional[str]:
        """Retrieves or creates a category ID for the specified category name.

        :return: The category ID if found; otherwise None.
        """
        category_id = get_category_context()

        StorageMethodology.select().add_new_category_folder(category_id)

        return category_id

    @staticmethod
    def determine_category(user_prompt: str, tag_category: Optional[str] = None) -> str:
        """
        Determine the category for the user prompt.

        :param user_prompt: The user's input prompt.
        :param tag_category: Optional tag category from the front end.
        :return: The determined category's name.
        """
        if not tag_category:
            category = CategoryManagement.categorise_input(user_prompt)
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
    CategoryManagement().generate_category_description("Please categorise this as 'testing'.")
