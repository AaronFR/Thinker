import logging

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from App import limiter
from App.extensions import user_key_func
from Constants.Constants import LIGHTLY_RESTRICTED, MODERATELY_RESTRICTED, MAX_FILE_SIZE, USER_LIGHTLY_RESTRICTED, \
    USER_DATA_LIMIT
from Constants.Exceptions import file_not_deleted
from Data.CategoryManagement import CategoryManagement
from Data.Configuration import Configuration
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Functionality.Organising import Organising
from Utilities.Decorators.AuthorisationDecorators import login_required
from Utilities.Routing import fetch_entity
from Utilities.Contexts import get_category_context
from Utilities.Validation import check_valid_uuid, space_in_content

files_bp = Blueprint('files', __name__)


# CRUD by ID


@files_bp.route('/file/<file_id>', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def get_file_by_id(file_id):
    return fetch_entity(nodeDB().get_file_by_id(file_id), "file")


@files_bp.route('/files', methods=['POST'])
@login_required
@limiter.limit(MODERATELY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def upload_files():
    """
    Accept multiple user files and categorise them together with the same category,
    then upload each file individually.

    ToDo: you might want to directly limit the size of incoming data
    ToDo: include option for category to be determined by category in tags (send tags)

    :returns: A Flask Response object containing a JSON representation of the processed message.
    """
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({'message': 'No files found in the request.'}), 400

    # ToDo: Notify frontend when user is close to limit - should be impossible for legitimate activity.
    user_data_size = nodeDB().retrieve_user_data_uploaded_size()
    if user_data_size > USER_DATA_LIMIT:
        new_user_data_size_in_gb = user_data_size / (1024 * 1024 * 1024)
        return jsonify({
            'message': f"Sorry, You've maxed our safety limit on total data uploaded of 1 GB. ({new_user_data_size_in_gb} GB) Please "
                       "delete unneeded files and/or get in contact"
        }), 400

    file_details = []
    samples = []
    content_aggregation = ""

    config = Configuration.load_config()
    bulk_upload_categorisation = config.get('files', {}).get("bulk_upload_categorisation")
    for file in files:
        if file.filename == '':
            return jsonify({'message': 'One or more files have no selected filename.'}), 400

        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        try:
            content = file.read().decode()
            sample_content = content[:500]  # Max 500 first characters are required for categorisation
        except Exception as decode_err:
            logging.exception(f"Decoding error for file {filename}: {decode_err}")
            return jsonify({'message': f"Error decoding file {filename}."}), 400

        if len(content) > MAX_FILE_SIZE:
            return jsonify({'message': f"File {filename} is too large. 10 MB allowed max."}), 400

        # Attach the files name and a sample of its contents for categorisation
        samples.append(filename + ": " + sample_content)
        content_aggregation += content

        content_size = len(content_aggregation)
        if content_size > MAX_FILE_SIZE:
            return jsonify({'message': f"Too much data uploaded at once. 10 MB allowed max."}), 400

        if not bulk_upload_categorisation:
            category = CategoryManagement.categorise_input(sample_content)
            CategoryManagement.possibly_create_new_category(category)
            category_id = get_category_context()
            file_details.append({'category_id': category_id, 'content': content, 'filename': filename})
        else:
            file_details.append({'content': content, 'filename': filename})

    if bulk_upload_categorisation:
        combined_content = "\n".join(samples)  # Combine all contents into one block for categorisation:

        category = CategoryManagement.categorise_input(combined_content)
        CategoryManagement.possibly_create_new_category(category)
        category_id = get_category_context()

        for file_detail in file_details:
            file_detail["category_id"] = category_id

    try:
        category_id = get_category_context()

        result_list = []
        for details in file_details:
            file_id = Organising.save_file(details['content'], category_id, details['filename'], overwrite=True)
            if file_id:
                result_list.append({
                    'category_id': details['category_id'],
                    'id': file_id,
                    'name': details['filename']
                })

        return jsonify({
            'message': 'Files uploaded successfully.',
            'category_id': category_id,
            'files': result_list
        }), 200

    except Exception as e:
        logging.exception(f"Error saving files: {e}")
        return jsonify({'message': 'File upload failed due to server error.'}), 500


@files_bp.route('/file/<file_id>', methods=['DELETE'])
@login_required
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def delete_file(file_id):
    """
    ToDo: Doesn't actually delete the file in local storage

    :param file_id: the UUID of the file to delete
    :return:
    """
    if not check_valid_uuid(file_id):
        return jsonify({"error": "Invalid file id"}), 400

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
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def list_files_in_category(category_name):
    if space_in_content(category_name):
        return jsonify({"error": "Invalid. Category names cannot have spaces in them"}), 400

    category_name = category_name.lower()
    return fetch_entity(nodeDB().get_files_by_category(category_name), "files")


# By File Address


@files_bp.route('/file_address/<file_category>/<file_name>', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def get_file_content_by_address(file_category, file_name):
    if space_in_content(file_category):
        return jsonify({"error": "Invalid. Category names cannot have spaces in them"}), 400
    if space_in_content(file_name):
        return jsonify({"error": "Invalid. File names cannot have spaces in them"}), 400

    full_path = str(file_category) + "/" + file_name

    logging.info(f"File node {file_category}/{file_name} content extracted")
    return fetch_entity(StorageMethodology.select().read_file(full_path), "content")