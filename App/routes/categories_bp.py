from flask import Blueprint, jsonify
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Utilities.Routing import fetch_entity
from Utilities.auth_utils import login_required

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/categories', methods=['GET'])
@login_required
def list_categories():
    """ List all categories for the user

    :return: A JSON response containing the list of categories.
    :raises: JSON response with error message on failure.
    """
    return fetch_entity(nodeDB().list_categories(), "categories")


@categories_bp.route('/categories_with_files', methods=['GET'])
@login_required
def list_categories_with_files():
    """ List all categories the user has with files.

    :return: A JSON response containing the list of categories with files.
    :raises: JSON response with error message on failure.
    """
    return fetch_entity(nodeDB().list_categories_with_files(), "categories")
