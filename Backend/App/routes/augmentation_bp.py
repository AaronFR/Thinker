import logging
from typing import List, Dict

from flask import Blueprint, jsonify, request

from Data.Files.StorageMethodology import StorageMethodology
from Functionality.Augmentation import Augmentation
from Utilities.AuthUtils import login_required
from Utilities.CostingUtils import balance_required
from Utilities.Routing import parse_and_validate_data

augmentation_bp = Blueprint('augmentation', __name__)

SELECT_WORKFLOW_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
    "tags": {"required": False, "type": Dict},
}
SELECT_PERSONA_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
}
AUGMENT_PROMPT_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
}
QUESTION_PROMPT_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
    "selected_messages": {"required": False, "type": List},
    "selected_files": {"required": False, "type": List},
}


@augmentation_bp.route('/augmentation/select_persona', methods=['POST'])
@login_required
@balance_required
def select_persona():
    """
    Will select an appropriate persona automatically based on the users input

    :return: A JSON object representing the selected persona
    """
    try:
        data = request.get_json()
        parsed_data = parse_and_validate_data(data, SELECT_WORKFLOW_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")

        selected_persona = Augmentation.select_persona(user_prompt).value

        return jsonify({"persona": selected_persona})
    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to select persona")
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/augmentation/select_workflow', methods=['POST'])
@login_required
@balance_required
def select_workflow():
    """
    Will select a workflow automatically, either based on tags or failing that an llm call

    :return: A JSON object representing the selected workflow
    """
    try:
        data = request.get_json()
        parsed_data = parse_and_validate_data(data, SELECT_WORKFLOW_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")
        tags = parsed_data.get("tags")

        selected_workflow = Augmentation.select_workflow(user_prompt, tags).value

        return jsonify({"workflow": selected_workflow})
    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to select workflow")
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/augmentation/augment_prompt', methods=['POST'])
@login_required
@balance_required
def augment_user_prompt():
    """
    Accept a user prompt and augment it in line with prompt engineering standards.

    :returns: A Flask Response object containing a JSON representation of the augmented message.
    """
    logging.info("augment_user_prompt triggered")

    try:
        data = request.get_json()
        parsed_data = parse_and_validate_data(data, AUGMENT_PROMPT_SCHEMA)

        logging.debug(f"Processing augmented prompt, data: {parsed_data}")
        user_prompt = parsed_data.get("user_prompt")

        augmented_response = Augmentation.augment_prompt(user_prompt)
        logging.info(f"Augmented response: \n{augmented_response}")

        return jsonify({"message": augmented_response})

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to augment message")
        return jsonify({"error": str(e)}), 500


@augmentation_bp.route('/augmentation/question_prompt', methods=['POST'])
@login_required
@balance_required
def question_user_prompt():
    """
    Accept a user prompt and generates a list of questions that *may* improve the llm's response

    :returns: A Flask Response object containing a JSON representation of the questions for the given message.
    """
    logging.info("question_user_prompt triggered")

    try:
        data = request.get_json()
        parsed_data = parse_and_validate_data(data, QUESTION_PROMPT_SCHEMA)
        user_prompt = parsed_data.get("user_prompt")
        selected_messages = parsed_data.get("selected_messages")
        selected_files = parsed_data.get("selected_files")

        reference_messages = None
        if selected_messages:
            reference_messages = []
            for message in selected_messages:
                reference_messages.append(
                    message.get("prompt") + "\nResponse:\n" + message.get("response"))

        reference_files = None
        if selected_files:
            reference_files = []
            for file in selected_files:
                file_category = file.get("category_id")
                file_name = file.get("name")
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
        logging.exception("Failed to generate questions for message")
        return jsonify({"error": str(e)}), 500




