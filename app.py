"""
Flask Backend Application

This module sets up a Flask server to serve a simple development message
in JSON format through the `/api/message` endpoint.
"""
import json
import logging
import os
from datetime import timedelta

import eventlet
import shortuuid

from Utilities.Encryption import hash_password, check_password

eventlet.monkey_patch()

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, decode_token, jwt_required, get_jwt_identity, \
    set_access_cookies, unset_jwt_cookies, create_refresh_token
from flask_socketio import SocketIO, emit
from functools import wraps

from werkzeug.utils import secure_filename

from Data.CategoryManagement import CategoryManagement
from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Functionality.Augmentation import Augmentation
from Functionality.Organising import Organising
from Personas.Coder import Coder
from Data.Configuration import Configuration
from Data.Pricing import Pricing
from Utilities.UserContext import set_user_context, get_user_context

logging.basicConfig(level=logging.DEBUG)

# Instantiate the Flask application
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # Access token expires in 15 minutes
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)     # Refresh token expires in 7 days
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['ENV'] = "development"

jwt = JWTManager(app)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

ERROR_NO_PROMPT = "No prompt found"
ERROR_NO_ID = "No user id found"
FILES_PATH = os.path.join(os.path.dirname(__file__), 'Data/FileData')
ACCESS_TOKEN_COOKIE = "access_token_cookie"
REFRESH_TOKEN_COOKIE = "refresh_token"

# ToDo: NodeDatabaseManagement should be instantiated at the class level if possible


# Authorisation

@app.route('/register', methods=['POST'])
def register():
    """
    ToDo: Add in user warnings or at least logging if a method fails to find a user in the db, failing a query

    :return:
    """
    data = request.json

    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    password_hash = hash_password(data.get('password'))
    if not data.get('password'):
        return jsonify({"error": "Password is required"}), 400

    node_db = NodeDatabaseManagement()
    user_id = str(shortuuid.uuid())

    if node_db.user_exists(email):
        logging.warning(f"Registration failed: User with email {email} already exists.")
        return jsonify({"error": "User with this email already exists"}), 409

    logging.info("Registering new user")
    registered = node_db.create_user(user_id, email, password_hash)
    if registered:
        logging.info("Successfully registered new user")
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        response = make_response(jsonify({"message": "User registration successful"}))
        response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, httponly=True, secure=True)
        response.set_cookie(REFRESH_TOKEN_COOKIE, refresh_token, httponly=True, secure=True, samesite="Strict")
        return response
    else:
        logging.error("Failed to register new user!")
        return jsonify({"Failure": "Failed to register user"}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    node_db = NodeDatabaseManagement()
    user_id = node_db.find_user_by_email(email)
    if not user_id:
        return jsonify({"error": "This email is not present in our systems"}), 400

    password = data.get("password")
    if not password:
        return jsonify({"error": "Password is required"}), 400
    password_hash = node_db.get_user_password_hash(user_id)
    if not check_password(password, password_hash):
        return jsonify({"error": "Incorrect password"}), 400

    try:
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, httponly=True, secure=True)
        response.set_cookie(REFRESH_TOKEN_COOKIE, refresh_token, httponly=True, secure=True, samesite="Strict")
        return response
    except Exception as e:
        return jsonify({"error": "Failed to login"}), 401


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Retrieve the JWT from the cookies
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            logging.info("No access_token cookie found")
            return jsonify({"status": "invalid", "error": "No token provided"}), 401

        user_id = decode_jwt(token)
        if not user_id:
            return jsonify({"status": "invalid", "error": "Invalid token"}), 401
        set_user_context(user_id)

        logging.debug(f"Decoded user_id: {user_id}")

        # Proceed with the request
        return fn(*args, **kwargs)

    return wrapper


@app.route('/auth/validate', methods=['GET'])
def validate_session():
    try:
        # Retrieve the JWT from the cookies
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            logging.info("No access_token cookie found")
            return jsonify({"status": "invalid", "error": "No token provided"}), 401

        user_id = decode_jwt(token)
        if not user_id:
            return jsonify({"status": "invalid", "error": "Invalid token"}), 401
        set_user_context(user_id)

        logging.debug(f"Decoded user_id: {user_id}")
        return jsonify({"status": "valid", "user_id": user_id}), 200
    except Exception as e:
        logging.exception("Error validating token")
        return jsonify({"status": "invalid", "error": "Unexpected error"}), 500


def decode_jwt(token):
    """
    Decode and validate the JWT token.
    """
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")  # 'sub' is typically used for user_id
        return user_id
    except Exception as e:
        logging.error(f"JWT validation error: {e}")
        return None


BLACKLIST = set()  # ToDo: Will need to be more robust


@app.route('/logout', methods=['POST'])
def logout():
    try:
        logging.info("Validating JWT for logout")
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            logging.info("No access_token cookie found")
            return jsonify({"status": "invalid", "error": "No token provided"}), 401
    except Exception as e:
        logging.exception("JWT validation failed")
        return jsonify({"error": "JWT validation failed"}), 401

    response = make_response(jsonify({"message": "Successfully logged out"}))
    unset_jwt_cookies(response)
    return response


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST


@app.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token missing"}), 401

    try:
        user_id = decode_token(refresh_token)["sub"]
        access_token = create_access_token(identity=user_id)

        response = make_response(jsonify({"message": "Token refreshed"}))
        response.set_cookie( "access_token", access_token, httponly=True, secure=True, samesite="Strict")
        return response
    except Exception as e:
        return jsonify({"error": "Invalid refresh token"}), 401


# Messages


@app.route('/messages/<category_name>', methods=['GET'])
@login_required
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
@login_required
def process_message(data):
    """
    Accept a user prompt and process it through the selected persona.
    ToDo: refresh tokens on streams are a bit difficult. Implement if its possible in the final version if its possible
     to not hit a regular automatically-refreshing request
    """
    logging.info(f"process_message triggered with data: {data}")
    node_db = NodeDatabaseManagement()

    try:
        user_prompt = data.get("prompt")
        if user_prompt is None:
            emit('error', {"error": ERROR_NO_PROMPT})
            return

        user_id = data.get("user_id")
        set_user_context(user_id)
        logging.info(f"Set user context: {get_user_context()}")
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
        response_message = selected_persona.query(user_prompt, file_references, tags)
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
        Organising.categorize_and_store_prompt(user_prompt, full_message, category)

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
@login_required
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

    :return:
    """
    user_id = get_user_context()
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
@login_required
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

    user_id = get_user_context()
    staged_file_path = os.path.join(FILES_PATH, user_id, filename)

    try:
        file.save(staged_file_path)
        return jsonify({'message': 'File uploaded successfully.', 'filename': filename}), 200
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'message': 'File upload failed due to server error.'}), 500


@app.route('/file/<file_id>', methods=['DELETE'])
@login_required
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


@app.route('/augmentation/question_prompt', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
