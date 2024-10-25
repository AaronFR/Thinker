"""
Flask Backend Application

This module sets up a Flask server to serve a simple development message
in JSON format through the `/api/message` endpoint.
"""
import logging
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from werkzeug.utils import secure_filename

from Data.CategoryManagement import CategoryManagement
from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Functionality.Augmentation import Augmentation
from Personas.Coder import Coder
from Data.Configuration import Configuration
from Data.Pricing import Pricing

logging.basicConfig(level=logging.DEBUG)

# Instantiate the Flask application
app = Flask(__name__)
CORS(app)

ERROR_NO_PROMPT = "No prompt found"
STAGING_AREA = os.path.join(os.path.dirname(__file__), 'thoughts', "0")

@app.route('/api/message', methods=['GET'])
def get_message():
    """
    Retrieve a simple development message.

    This endpoint returns a JSON object containing a message to inform 
    users of the current development status of the site.

    :returns: A Flask Response object containing a JSON representation 
              of the development message.
    """
    return jsonify({"message": "Hello, this site is in development!"})


@app.route('/api/message', methods=['POST'])
def process_message():
    """
    Accept a user prompt and process it through the selected persona.

    :returns: A Flask Response object containing a JSON representation of the processed message.
    """
    logging.info("process_message triggered")
    node_db = NodeDatabaseManagement()

    try:
        data = request.get_json()
        user_prompt = data.get("prompt")
        if user_prompt is None:
            return jsonify({"error": ERROR_NO_PROMPT}), 400

        # ToDo: additional_qa should be sent as an additional user message or system message (requires system redesign)
        additional_qa = data.get("additionalQA")
        if additional_qa:
            user_prompt = user_prompt + "\nAdditional Q&A context: \n" + additional_qa

        files = data.get("files")
        file_references = []
        if files:
            for file in files:
                file_with_category = node_db.get_file_by_id(file.get("id"))
                for record in file_with_category:
                    file_system_address = f"{record['category']}\\{record['name']}"
                    file_references.append(file_system_address)

        selected_persona = get_selected_persona(data) 
        response_message = selected_persona.query(user_prompt, file_references)
        logging.info("Response generated: %s", response_message)

        # ToDo: should be an ancillary side job, currently slows down recieving a response if the database doesn't respond quickly
        selected_category = node_db.create_user_prompt_node(user_prompt, response_message)

        categoryManagement = CategoryManagement()
        categoryManagement.stage_files(user_prompt, selected_category)

        return jsonify({"message": response_message})
    
    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to process message")
        return jsonify({"error": str(e)}), 500


def get_selected_persona(data):
    """ Determine the selected persona or default to 'coder'. """
    persona_selection = data.get("persona")
    if persona_selection == 'coder':
        persona = Coder("Coder")
    if persona_selection not in ['coder']:
        logging.warning("Invalid persona selected, defaulting to coder")
        return Coder("Default")
    return persona


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


@app.route('/content/<file_category>/<file_name>', methods=['GET'])
def get_file_content(file_category, file_name):
    try:
        full_path = str(file_category) + "/" + file_name
        content = FileManagement.read_file_full_address(full_path)

        logging.info(f"File node {file_category}/{file_name} content extracted")
        return jsonify({"content": content}), 200
    except Exception as e:
        logging.exception(f"Failed to get content for {file_category}/{file_name}")
        return jsonify({"error": str(e)}), 500


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


@app.route('/api/file', methods=['POST'])
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

    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(file.filename)
    file_path = os.path.join(STAGING_AREA, filename)

    try:
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully.', 'filename': filename}), 200
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'message': 'File upload failed due to server error.'}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(STAGING_AREA)
        return jsonify({'files': files}), 200
    except Exception as e:
        print(f"Error listing files: {e}")
        return jsonify({'message': 'Failed to retrieve files.'}), 500


@app.route('/api/augment_prompt', methods=['POST'])
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


@app.route('/api/question_prompt', methods=['POST'])
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


@app.route('/pricing/session', methods=['GET'])
def get_session_cost():
    try:
        logging.info("Extracting current session cost")
        cost = Pricing.get_session_cost()

        return jsonify({"cost": cost}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/categories', methods=['GET'])
def list_categories():
    try:
        node_db = NodeDatabaseManagement()
        categories = node_db.list_user_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/categories_with_files', methods=['GET'])
def list_categories_with_files():
    try:
        node_db = NodeDatabaseManagement()
        categories = node_db.list_user_categories_with_files()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/categories/<category_name>/messages', methods=['GET'])
def get_messages(category_name):
    try:
        category_name = category_name.lower()
        node_db = NodeDatabaseManagement()
        messages = node_db.get_messages_by_category(category_name)
        messages_list = [
            {"id": record["id"],
             "prompt": record["prompt"],
             "response": record["response"],
             "time": record["time"]} for record in messages]

        return jsonify({"messages": messages_list}), 200
    except Exception as e:
        logging.exception(f"Failed to get messages for category, {category_name}")
        return jsonify({"error": str(e)}), 500


@app.route('/categories/<category_name>/files', methods=['GET'])
def get_files(category_name):
    try:
        category_name = category_name.lower()
        node_db = NodeDatabaseManagement()
        files = node_db.get_files_by_category(category_name)
        files_list = [
            {"id": record["id"],
             "category_id": record["category_id"],
             "name": record["name"],
             "summary": record["summary"],
             "structure": record["structure"],
             "time": record["time"]} for record in files]

        return jsonify({"files": files_list}), 200
    except Exception as e:
        logging.exception(f"Failed to get messages for category, {category_name}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logging.info("Back end is running")
    # Run the Flask application in debugging mode (only for development purposes)
    app.run(debug=True)