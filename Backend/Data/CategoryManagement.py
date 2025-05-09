import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import shortuuid
from flask import copy_current_request_context

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Constants.Constants import RESULT_AS_TAG_REGEX, DEFAULT_CATEGORY
from Constants.Exceptions import failure_to_suggest_colour_for_category, failure_to_create_instructions_for_category
from Data.Configuration import Configuration
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Utilities import Colour
from Constants.Instructions import DEFAULT_USER_CATEGORISATION_INSTRUCTIONS, categorisation_inputs, \
    SELECT_COLOUR_SYSTEM_MESSAGE, CATEGORY_INSTRUCTIONS_SYSTEM_MESSAGE, category_instructions_prompt, \
    categorisation_system_messages
from Utilities.Contexts import set_category_context, get_category_context, set_message_context, set_user_context, \
    get_user_context, get_message_context
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
        :param user_prompt: used as context for deciding the category's instructions
        :return:
        """
        categories = nodeDB().list_category_names()

        if category not in categories:
            category_id, instructions, color = CategoryManagement.define_new_category(category, user_prompt)
            nodeDB().create_category_and_user_prompt(category_id, category, instructions, color)
        else:
            category_id = nodeDB().get_category_id(category)
            nodeDB().create_user_prompt_node(category)

        set_category_context(category_id)

    @staticmethod
    def possibly_create_new_category(category_name: str) -> str | None:
        """
        Checks if a category exists by name. If not, creates it using define_new_category.
        Returns the category ID (existing or newly created), or None if creation fails.
        """
        if not category_name or not isinstance(category_name, str) or category_name.strip() == "":
            logging.warning("Attempted to create or find category with invalid name.")
            return None

        existing_category_id = nodeDB().get_category_id(category_name)

        if existing_category_id:
            logging.debug(f"Category '{category_name}' already exists with ID {existing_category_id}.")

            set_category_context(existing_category_id)
            return existing_category_id
        else:
            # Category does not exist, try to create it
            logging.info(f"Category '{category_name}' not found. Attempting to create.")
            try:
                new_category_id, instructions, color = CategoryManagement.define_new_category(category_name)

                if nodeDB().create_category(new_category_id, category_name, instructions, color):
                    logging.info(f"Successfully created category '{category_name}' with ID {new_category_id}.")

                    set_category_context(new_category_id)
                    return new_category_id
                else:
                    logging.error(f"Defined category '{category_name}' but failed to save it to the database.")
                    return None
            except Exception as e:
                logging.exception(f"Error creating category '{category_name}': {e}")
                return None

    @staticmethod
    def define_new_category(category: str, additional_context: str = ""):
        """
        Defines a new category, generating its color and system instructions concurrently.

        :param category: The category name
        :param additional_context: The user's prompt which is used as context when creating system instructions for the
         categories.
        :return: The id, instructions and color of the new category
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

        def wrapped_process_generate_category_instructions(category, additional_context, user_id, category_id, message_id):
            set_user_context(user_id)
            set_category_context(category_id)
            set_message_context(message_id)

            return CategoryManagement.generate_category_instructions(
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
            instructions_future = executor.submit(
                copy_current_request_context(wrapped_process_generate_category_instructions),
                category,
                additional_context,
                user_id,
                category_id,
                message_id
            )

            logging.info(f"Tasks submitted for '{category}'. Waiting for results...")
            try:
                instructions_result = instructions_future.result()
                logging.info(f"Instructions result received for '{category}'.")
                color_result = color_future.result()
                logging.info(f"Color result received for '{category}'.")

            except Exception as e:
                logging.error(f"Error during concurrent category generation for '{category}': {e}", exc_info=True)
                raise

        return category_id, instructions_result, color_result

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
    def default_instructions(category_name: str) -> str:
        """
        Provides a default instructions for the category if AI fails.

        :param category_name: The name of the category.
        :return: default system instructions.
        """
        default = f"A category for {category_name.lower()} related items."
        logging.debug(f"Default instructions for '{category_name}': {default}")
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
        use_ai = config['category'].get("ai_colour", False)
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
    def generate_category_instructions(category_name: str, additional_context: str = "") -> str:
        """
        Generates a system instructions for future prompts in the given category using AI, if configured to do so.
        Otherwise, a blank instruction will be created which the user can fill out themselves if they want.

        :param category_name: The name of the category to describe.
        :param additional_context: Optionally add the user prompt for additional context
        :return: A short string of instructions for the category.
        """
        config = Configuration.load_config()
        generate_category_system_message = config['category'].get("generate_category_system_message", False)
        try:
            if generate_category_system_message:
                instructions = AiOrchestrator().execute(
                    [CATEGORY_INSTRUCTIONS_SYSTEM_MESSAGE],
                    [
                        category_instructions_prompt(category_name),
                        additional_context,
                    ]
                )
                instructions = instructions.strip()

                logging.debug(f"AI-generated instructions for '{category_name}': {instructions}")
                return instructions
            else:
                return ""
        except Exception:
            logging.exception(failure_to_create_instructions_for_category(category_name))
            return CategoryManagement.default_instructions(category_name)


if __name__ == '__main__':
    CategoryManagement().generate_category_instructions("Please categorise this as 'testing'.")
