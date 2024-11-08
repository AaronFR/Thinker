"""
Flask Backend Application

This module sets up a Flask server to serve a simple development message
in JSON format through the `/api/message` endpoint.
"""
import json
import logging
import os

import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from werkzeug.utils import secure_filename

from Data.CategoryManagement import CategoryManagement
from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Functionality.Augmentation import Augmentation
from Functionality.Organising import Organising
from Personas.Coder import Coder
from Data.Configuration import Configuration
from Data.Pricing import Pricing

logging.basicConfig(level=logging.DEBUG)

# Instantiate the Flask application
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

ERROR_NO_PROMPT = "No prompt found"
ERROR_NO_ID = "No user id found"
FILES_PATH = os.path.join(os.path.dirname(__file__), 'Data/FileData')


# Messages


@app.route('/messages/<category_name>', methods=['GET'])
def get_messages(category_name):
    try:
        category_name = category_name.lower()
        node_db = NodeDatabaseManagement()
        messages_list = node_db.get_messages_by_category(category_name)

        return jsonify({"messages": messages_list}), 200
    except Exception as e:
        logging.exception(f"Failed to get messages for category, {category_name}")
        return jsonify({"error": str(e)}), 500


@socketio.on('start_stream')
def process_message(data):
    """
    Accept a user prompt and process it through the selected persona.
    """
    logging.info(f"process_message triggered with data: {data}")
    node_db = NodeDatabaseManagement()

    try:
        user_prompt = data.get("prompt")
        if user_prompt is None:
            emit('error', {"error": ERROR_NO_PROMPT})
            return

        user_id = data.get("user_id")
        if user_id is None:
            emit('error', {"error": ERROR_NO_ID})
            return

        additional_qa = data.get("additionalQA")
        if additional_qa:
            user_prompt = f"{user_prompt}\nAdditional Q&A context: \n{additional_qa}"

        tags = data.get('tags', {})
        if isinstance(tags, str):
            tags = json.loads(tags)
            if "tags" in tags:
                tags = tags["tags"]
        logging.info(f"Loading the following tags while processing the prompt: {tags}")

        files = data.get("files")
        file_references = Organising.process_files(files)

        categoryManagement = CategoryManagement()
        tag_category = tags.get("category")
        if tag_category:
            logging.info(f"tag specified category: {tag_category}")
            category = tag_category
        else:
            category = categoryManagement.categorise_prompt_input(user_prompt)
            tags["category"] = category

        selected_persona = get_selected_persona(data)
        response_message = selected_persona.query(user_id, user_prompt, file_references, tags)
        logging.info("Response generated: %s", response_message)

        chunk_content = []
        for chunk in response_message:
            if 'content' in chunk:
                content = chunk['content']
                chunk_content += content
                emit('response', {'content': content})
            elif 'stream_end' in chunk:
                emit('stream_end')
                break  # Exit the loop after emitting 'stream_end

        full_message = "".join(chunk_content)
        # ToDo: should be an ancillary side job, currently slows down recieving a response if the database doesn't respond quickly
        Organising.categorize_and_store_prompt(user_prompt, full_message, user_id, category)

        logging.info(f"response message: {response_message}")

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        emit('error', {"error": str(ve)})
    except Exception as e:
        logging.exception("Failed to process message")
        emit('error', {"error": str(e)})


@app.route('/messages/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        node_db = NodeDatabaseManagement()
        node_db.delete_message_by_id(message_id)

        logging.info(f"User prompt node {message_id} deleted")
        return jsonify({"message": f"Message {message_id} deleted successfully"}), 200
    except Exception as e:
        logging.exception(f"Failed to delete message {message_id}")
        return jsonify({"error": str(e)}), 500


# Categories


@app.route('/categories', methods=['GET'])
def list_categories():
    try:
        node_db = NodeDatabaseManagement()
        categories = node_db.list_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/categories_with_files', methods=['GET'])
def list_categories_with_files():
    try:
        node_db = NodeDatabaseManagement()
        categories = node_db.list_categories_with_files()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Files


@app.route('/files/<category_name>', methods=['GET'])
def get_files(category_name):
    try:
        category_name = category_name.lower()
        node_db = NodeDatabaseManagement()
        files_list = node_db.get_files_by_category(category_name)

        return jsonify({"files": files_list}), 200
    except Exception as e:
        logging.exception(f"Failed to get messages for category, {category_name}")
        return jsonify({"error": str(e)}), 500

@app.route('/file/<file_category>/<file_name>', methods=['GET'])
def get_file_content(file_category, file_name):
    try:
        full_path = str(file_category) + "/" + file_name
        content = FileManagement.read_file_full_address(full_path)

        logging.info(f"File node {file_category}/{file_name} content extracted")
        return jsonify({"content": content}), 200
    except Exception as e:
        logging.exception(f"Failed to get content for {file_category}/{file_name}")
        return jsonify({"error": str(e)}), 500


@app.route('/list_staged_files', methods=['GET'])
def list_files():
    """
    Lists the staged files for the user on prompt submission
    ToDo: The user id and user id staging folder will need to be created on account creation

    :return:
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'User ID is required.'}), 400

    user_folder = os.path.join(FILES_PATH, user_id)

    try:
        if os.path.exists(user_folder):
            files = os.listdir(user_folder)
            return jsonify({'files': files}), 200
        else:
            return jsonify({'message': 'User folder not found.'}), 404
    except Exception as e:
        print(f"Error listing files for user {user_id}: {e}")
        return jsonify({'message': 'Failed to retrieve files.'}), 500


@app.route('/file', methods=['POST'])
def upload_file():
    """
    Accept a user file and try uploading it for future reference.

    :returns: A Flask Response object containing a JSON representation of the processed message.
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file.'}), 400

    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(file.filename)
    staged_file_path = os.path.join(FILES_PATH, user_id, filename)

    try:
        file.save(staged_file_path)
        return jsonify({'message': 'File uploaded successfully.', 'filename': filename}), 200
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'message': 'File upload failed due to server error.'}), 500


@app.route('/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        node_db = NodeDatabaseManagement()
        node_db.delete_file_by_id(file_id)

        logging.info(f"File node {file_id} deleted")
        return jsonify({"message": f"File {file_id} deleted successfully"}), 200
    except Exception as e:
        logging.exception(f"Failed to delete file {file_id}")
        return jsonify({"error": str(e)}), 500


# Augmentation


def get_selected_persona(data):
    """ Determine the selected persona or default to 'coder'. """
    persona_selection = data.get("persona")
    if persona_selection == 'coder':
        persona = Coder("Coder")
    if persona_selection not in ['coder']:
        logging.warning("Invalid persona selected, defaulting to coder")
        return Coder("Default")
    return persona


@app.route('/augmentation/augment_prompt', methods=['POST'])
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


@app.route('/augmentation/question_prompt', methods=['POST'])
def question_user_prompt():
    """
    Accept a user prompt and generates a list of questions that *may* improve the llm's response

    :returns: A Flask Response object containing a JSON representation of the questions for the given message.
    """
    logging.info("question_user_prompt triggered")

    try:
        data = request.get_json()
        logging.debug(f"Genearting questions against user prompt, data: {data}")

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


@app.route('/data/config', methods=['GET'])
def load_config():
    """
    Load the configuration from the YAML file and return it as a JSON response.

    This endpoint retrieves the entire application configuration, stored in
    a YAML file, and returns it as a JSON object. This is useful for reading
    the current settings, such as dark mode preferences, without modifying
    the configuration.

    :returns: JSON response containing the configuration dictionary.
    """
    try:
        config = Configuration.load_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/data/config', methods=['POST'])
def update_config():
    """
    Load the configuration from the YAML file and return it as a JSON response.

    This endpoint retrieves the entire application configuration, stored in
    a YAML file, and returns it as a JSON object. This is useful for reading
    the current settings, such as dark mode preferences, without modifying
    the configuration.

    :returns: JSON response containing the configuration dictionary.
    """
    try:
        logging.info("trying to update config")
        data = request.json
        if not data:
            raise ValueError("No JSON data received")

        field = data.get('field')
        value = data.get('value')
        if not field or value is None:
            return jsonify({'error': 'Field and value are required'}), 400

        Configuration.update_config_field(field, value)
        return jsonify({"message": f"Config - {field}: {value} updated successfully"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Costing


@app.route('/pricing/session', methods=['GET'])
def get_session_cost():
    try:
        logging.info("Extracting current session cost")
        cost = Pricing.get_session_cost()

        return jsonify({"cost": cost}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logging.info("Back end is running")
    # Correctly run the Flask application with SocketIO
    socketio.run(app, debug=True)
