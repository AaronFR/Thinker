import json
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

    config = Configuration.load_config()
    use_tags_category = config.get("files", {}).get("use_tags_category", True)
    bulk_upload_categorisation = config.get('files', {}).get("bulk_upload_categorisation")

    tags_category_name = None
    if use_tags_category:
        tags_json = json.loads(request.form.get('tags', '{}'))
        tags_category_name = tags_json.get("category")

    processed_files_data = []
    samples_for_bulk_categorization = []
    cumulative_upload_size = 0

    # Process and Validate Files
    for file in files:
        if not file or not file.filename:
            return jsonify({'message': 'One or more files have no selected filename.'}), 400

        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            logging.warning(f"Could not decode file {filename} as UTF-8.")
            return jsonify({'message': f"Error decoding file {filename}. Ensure it is UTF-8 encoded."}), 400
        except Exception as decode_err:
            logging.exception(f"Decoding error for file {filename}: {decode_err}")
            return jsonify({'message': f"Error decoding file {filename}."}), 500

        content_size_bytes = len(content.encode('utf-8'))

        if content_size_bytes > MAX_FILE_SIZE:
            return jsonify({'message': f"File {filename} is too large. 10 MB allowed max."}), 400

        cumulative_upload_size += content_size_bytes

        processed_files_data.append({
            'content': content,
            'filename': filename,
            'sample': content[:500]  # Keep sample for potential individual categorization
        })

        if bulk_upload_categorisation and not tags_category_name:
            samples_for_bulk_categorization.append(filename + ": " + processed_files_data[-1]['sample'])

    if not processed_files_data:
        return jsonify({'message': 'No valid files processed.'}), 400

    # Determine Category
    final_category_id = None
    category_name_to_use = None

    if tags_category_name:
        category_name_to_use = tags_category_name
        logging.info(f"Using category '{category_name_to_use}' from tags.")

        final_category_id = CategoryManagement.possibly_create_new_category(category_name_to_use)
        if not final_category_id:
            return jsonify(
                {'message': f"Failed to process category specified in tags: {tags_category_name}"}), 500
    elif bulk_upload_categorisation:
        if not samples_for_bulk_categorization:
            logging.error("Bulk categorization enabled, but no samples collected (maybe all files were empty?).")
            return jsonify({'message': 'Cannot perform bulk categorization with no file content.'}), 400

        combined_samples = "\n".join(samples_for_bulk_categorization)
        category_name_to_use = CategoryManagement.categorise_input(combined_samples)
        logging.info(f"Using category '{category_name_to_use}' determined from bulk analysis.")
        final_category_id = CategoryManagement.possibly_create_new_category(category_name_to_use)
        if not final_category_id:
            return jsonify(
                {'message': f"Failed to process category determined from bulk analysis: {category_name_to_use}"}), 500

    # Save File to Storage
    result_list = []
    saved_category_id = final_category_id  # Use the determined ID if available, otherwise it will be set per file

    try:
        for file_data in processed_files_data:
            category_id_for_this_file = final_category_id

            if category_id_for_this_file is None:
                individual_category_name = CategoryManagement.categorise_input(file_data['sample'])
                logging.info(f"Determined category '{individual_category_name}' for file '{file_data['filename']}'.")
                category_id_for_this_file = CategoryManagement.possibly_create_new_category(individual_category_name)

                if not category_id_for_this_file:
                    logging.error(
                        f"Failed to determine or create category for file {file_data['filename']}. Skipping file.")
                    continue  # Skip this file

            saved_category_id = category_id_for_this_file
            file_id = Organising.save_file(
                content=file_data['content'],
                category_id=category_id_for_this_file,
                filename=file_data['filename'],
                overwrite=True
            )

            if file_id:
                result_list.append({
                    'category_id': category_id_for_this_file,
                    'id': file_id,
                    'name': file_data['filename']
                })
            else:
                logging.error(
                    f"Failed to save file node for {file_data['filename']} in category {category_id_for_this_file}")

        if not result_list:
            return jsonify({'message': 'Files were processed but none could be saved successfully.'}), 500

        return jsonify({
            'message': f'{len(result_list)} file(s) uploaded successfully.',
            'category_id': saved_category_id,  # ID of the category used (might be last one if mixed)
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