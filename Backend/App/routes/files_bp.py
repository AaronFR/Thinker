import logging
import os
import sys

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from App import limiter
from Constants.Constants import LIGHTLY_RESTRICTED, MODERATELY_RESTRICTED, MAX_FILE_SIZE
from Constants.Exceptions import file_not_deleted
from Data.CategoryManagement import CategoryManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Functionality.Organising import Organising
from Utilities.AuthUtils import login_required
from Utilities.Routing import fetch_entity
from Utilities.Contexts import get_user_context, get_category_context

files_bp = Blueprint('files', __name__)


# CRUD by ID


@files_bp.route('/file/<file_id>', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
def get_file_by_id(file_id):
    return fetch_entity(nodeDB().get_file_by_id(file_id), "file")


@files_bp.route('/file', methods=['POST'])
@login_required
@limiter.limit(MODERATELY_RESTRICTED)
def upload_file():
    """
    Accept a user file and try uploading it for staging

    :returns: A Flask Response object containing a JSON representation of the processed message.
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file.'}), 400
    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(file.filename)

    content = file.read().decode()
    if sys.getsizeof(content) > MAX_FILE_SIZE:
        raise Exception("File is far too large. 10 MB max.")

    category = CategoryManagement.categorise_input(content)
    CategoryManagement.possibly_create_new_category(category)
    file_path = os.path.join(get_category_context(), filename)

    try:
        Organising.save_file(content, category, file_path, overwrite=True)
        return jsonify({'message': 'File uploaded successfully.', 'filename': filename}), 200
    except Exception as e:
        logging.info(f"Error saving file: {e}")
        return jsonify({'message': 'File upload failed due to server error.'}), 500


@files_bp.route('/file/<file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """
    ToDo: Doesn't actually delete the file in local storage

    :param file_id: the UUID of the file to delete
    :return:
    """
    try:
        nodeDB().delete_file_by_id(file_id)

        logging.info(f"File node {file_id} deleted")
        return jsonify({"message": f"File {file_id} deleted successfully"}), 200
    except Exception as e:
        logging.exception(file_not_deleted(file_id))
        return jsonify({"error": str(e)}), 500


# List files


@files_bp.route('/files/category/<category_name>', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
def list_files_in_category(category_name):
    category_name = category_name.lower()
    return fetch_entity(nodeDB().get_files_by_category(category_name), "files")


@files_bp.route('/files/list_staged_files', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
def list_staged_files():
    """
    Lists the staged files for the user on prompt submission

    :return:
    """
    return fetch_entity(StorageMethodology.select().list_staged_files(), "files")


# By File Address


@files_bp.route('/file_address/<file_category>/<file_name>', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
def get_file_content_by_address(file_category, file_name):
    full_path = str(file_category) + "/" + file_name

    logging.info(f"File node {file_category}/{file_name} content extracted")
    return fetch_entity(StorageMethodology.select().read_file(full_path), "content")