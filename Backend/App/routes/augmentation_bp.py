"""
As in prompt augmentation
Stores a variety of features for improving the users prompts and helping the user write it, before it's submitted.
"""


import logging
from typing import List, Dict

from flask import Blueprint, jsonify, request

from App import limiter
from App.extensions import user_key_func
from Constants.Constants import MODERATELY_RESTRICTED, USER_MODERATELY_RESTRICTED
from Constants.Exceptions import FAILURE_TO_SELECT_WORKER, FAILURE_TO_SELECT_WORKFLOW, FAILURE_TO_AUTO_ENGINEER_PROMPT, \
    FAILURE_TO_QUESTION_PROMPT, FAILURE_TO_SELECT_CATEGORY
from Data.CategoryManagement import CategoryManagement
from Data.Files.StorageMethodology import StorageMethodology
from Functionality.Augmentation import Augmentation
from Utilities.Contexts import set_functionality_context
from Utilities.Decorators.AuthorisationDecorators import login_required
from Utilities.Decorators.PaymentDecorators import balance_required
from Utilities.Routing import parse_and_validate_data
from Utilities.Validation import sanitise_identifier

augmentation_bp = Blueprint('augmentation', __name__, url_prefix='/augmentation')

USER_PROMPT_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
}
USER_PROMPT_AND_TAGS_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
    "tags": {"required": False, "type": Dict},
}
USER_PROMPT_AND_TAGS_AND_FILES_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
    "tags": {"required": False, "type": Dict},
    "selected_files": {"required": False, "type": List},
}
USER_PROMPT_MESSAGES_AND_FILES_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
    "selected_messages": {"required": False, "type": List},
    "selected_files": {"required": False, "type": List},
}


@augmentation_bp.route('/select_worker', methods=['POST'])
@login_required
@balance_required
@limiter.limit(MODERATELY_RESTRICTED)
@limiter.limit(USER_MODERATELY_RESTRICTED, key_func=user_key_func)
def select_worker():
    """
    Will select an appropriate worker automatically based on the users input

    :return: A JSON object representing the selected worker
    """
    try:
        set_functionality_context("select_worker")

        data = request.get_json()
        parsed_data = parse_and_validate_data(data, USER_PROMPT_AND_TAGS_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")

        selected_worker = Augmentation.select_worker(user_prompt)

        return jsonify({"worker": selected_worker})
    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception(FAILURE_TO_SELECT_WORKER)
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/select_workflow', methods=['POST'])
@login_required
@balance_required
@limiter.limit(MODERATELY_RESTRICTED)
@limiter.limit(USER_MODERATELY_RESTRICTED, key_func=user_key_func)
def select_workflow():
    """
    Will select a workflow automatically, either based on tags or failing that an llm call

    :return: A JSON object representing the selected workflow
    """
    try:
        set_functionality_context("select_workflow")

        data = request.get_json()
        parsed_data = parse_and_validate_data(data, USER_PROMPT_AND_TAGS_AND_FILES_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")
        tags = parsed_data.get("tags")
        selected_files = parsed_data.get("selected_files", None)

        selected_workflow = Augmentation.select_workflow(user_prompt, tags, selected_files).value

        return jsonify({"workflow": selected_workflow})
    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception(FAILURE_TO_SELECT_WORKFLOW)
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/select_category', methods=['POST'])
@login_required
@balance_required
@limiter.limit(MODERATELY_RESTRICTED)
@limiter.limit(USER_MODERATELY_RESTRICTED, key_func=user_key_func)
def select_category():
    """
    Selects an appropriate category based on the input prompt
    """
    try:
        data = request.get_json()
        parsed_data = parse_and_validate_data(data, USER_PROMPT_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")

        selected_category = CategoryManagement.categorise_input(user_prompt)

        return jsonify({"category": selected_category})
    except Exception as e:
        logging.exception(FAILURE_TO_SELECT_CATEGORY)
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/auto_engineer_prompt', methods=['POST'])
@login_required
@balance_required
@limiter.limit(MODERATELY_RESTRICTED)
@limiter.limit(USER_MODERATELY_RESTRICTED, key_func=user_key_func)
def auto_engineer_user_prompt():
    """
    Accept a user prompt and augment it in line with prompt engineering standards.

    :returns: A Flask Response object containing a JSON representation of the augmented message.
    """
    logging.info("augment_user_prompt triggered")

    try:
        set_functionality_context("augmentation")

        data = request.get_json()
        parsed_data = parse_and_validate_data(data, USER_PROMPT_SCHEMA)

        logging.debug(f"Processing augmented prompt, data: {parsed_data}")
        user_prompt = parsed_data.get("user_prompt")

        augmented_response = Augmentation.augment_prompt(user_prompt)
        logging.info(f"Augmented response: \n{augmented_response}")

        return jsonify({"message": augmented_response})

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception(FAILURE_TO_AUTO_ENGINEER_PROMPT)
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/question_prompt', methods=['POST'])
@login_required
@balance_required
@limiter.limit(MODERATELY_RESTRICTED)
@limiter.limit(USER_MODERATELY_RESTRICTED, key_func=user_key_func)
def question_user_prompt():
    """
    Accept a user prompt and generates a list of questions that *may* improve the llm's response

    :returns: A Flask Response object containing a JSON representation of the questions for the given message.
    """
    logging.info("question_user_prompt triggered")

    try:
        set_functionality_context("questioning")

        data = request.get_json()
        parsed_data = parse_and_validate_data(data, USER_PROMPT_MESSAGES_AND_FILES_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")
        if not user_prompt:
            raise Exception("User prompt not found!(?)")

        selected_messages = parsed_data.get("selected_messages")
        selected_files = parsed_data.get("selected_files")

        reference_messages = None
        prompt_key = "prompt"
        response_key = "response"
        if selected_messages:
            reference_messages = []
            for message in selected_messages:
                reference_messages.append(
                    f"{message.get(prompt_key)} \n"
                    "Response: \n"
                    f"{message.get(response_key)}"
                )

        reference_files = None
        if selected_files:
            reference_files = []
            for file in selected_files:
                # ToDo: Should be a helper method
                file_category = sanitise_identifier(file.get("category_id"))
                file_name = sanitise_identifier(file.get("name"))
                full_path = str(file_category) + "/" + file_name

                file_contents = StorageMethodology.select().read_file(full_path)
                reference_files.append(f"<{file_name}>\n{file_contents}\n</{file_name}>")

        logging.debug(f"Generating questions against user prompt, data: {parsed_data}")
        questions_for_prompt = Augmentation.question_user_prompt(user_prompt, reference_messages, reference_files)
        logging.info(f"questions for user prompt: \n{questions_for_prompt}")

        return jsonify({"message": questions_for_prompt})

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception(FAILURE_TO_QUESTION_PROMPT)
        return jsonify({"error": str(e)}), 500




