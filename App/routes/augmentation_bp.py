import logging

from flask import Blueprint, jsonify, request

from Functionality.Augmentation import Augmentation
from Utilities.AuthUtils import login_required
from Utilities.Routing import parse_and_validate_data

augmentation_bp = Blueprint('augmentation', __name__)

AUGMENT_PROMPT_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
}
QUESTION_PROMPT_SCHEMA = {
    "user_prompt": {"required": True, "type": str},
}


@augmentation_bp.route('/augmentation/augment_prompt', methods=['POST'])
@login_required
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

        logging.debug(f"Generating questions against user prompt, data: {parsed_data}")
        questions_for_prompt = Augmentation.question_user_prompt(user_prompt)
        logging.info(f"questions for user prompt: \n{questions_for_prompt}")

        return jsonify({"message": questions_for_prompt})

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to generate questions for message")
        return jsonify({"error": str(e)}), 500
