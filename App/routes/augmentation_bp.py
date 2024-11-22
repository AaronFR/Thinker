import logging

from flask import Blueprint, jsonify, request

from Functionality.Augmentation import Augmentation
from Utilities.AuthUtils import login_required

augmentation_bp = Blueprint('augmentation', __name__)


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
        logging.debug(f"Processing augmented prompt, data: {data}")

        user_prompt = data.get("user_prompt")
        if user_prompt is None:
            return jsonify({"error": "No user prompt provided"}), 400

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
        logging.debug(f"Generating questions against user prompt, data: {data}")

        user_prompt = data.get("user_prompt")
        if user_prompt is None:
            return jsonify({"error": "No user prompt provided"}), 400

        questions_for_prompt = Augmentation.question_user_prompt(user_prompt)
        logging.info(f"questions for user prompt: \n{questions_for_prompt}")

        return jsonify({"message": questions_for_prompt})

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to generate questions for message")
        return jsonify({"error": str(e)}), 500
