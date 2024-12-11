import logging
import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from Data.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Utilities.AuthUtils import login_required
from Utilities.Routing import fetch_entity
from Utilities.Contexts import get_user_context


files_bp = Blueprint('files', __name__)
FILES_PATH = os.path.join(os.path.dirname(__file__), '../../Data/FileData')


@files_bp.route('/files/<category_name>', methods=['GET'])
@login_required
def get_files(category_name):
    category_name = category_name.lower()
    return fetch_entity(nodeDB().get_files_by_category(category_name), "files")


@files_bp.route('/file/<file_category>/<file_name>', methods=['GET'])
@login_required
def get_file_content(file_category, file_name):
    full_path = str(file_category) + "/" + file_name

    logging.info(f"File node {file_category}/{file_name} content extracted")
    return fetch_entity(FileManagement.read_file_full_address(full_path), "content")


@files_bp.route('/list_staged_files', methods=['GET'])
@login_required
def list_files():
    """
    Lists the staged files for the user on prompt submission

    :return:
    """
    user_id = get_user_context()
    logging.info(f"🤔 {FILES_PATH}, {user_id}")
    user_folder = os.path.join(FILES_PATH, user_id)

    if not os.path.exists(user_folder):
        return jsonify({'message': 'User folder not found.'}), 404

    return fetch_entity(os.listdir(user_folder), "files")


@files_bp.route('/file', methods=['POST'])
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


@files_bp.route('/file/<file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    try:
        nodeDB().delete_file_by_id(file_id)

        logging.info(f"File node {file_id} deleted")
        return jsonify({"message": f"File {file_id} deleted successfully"}), 200
    except Exception as e:
        logging.exception(f"Failed to delete file {file_id}")
        return jsonify({"error": str(e)}), 500
