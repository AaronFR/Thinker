from flask import Blueprint, jsonify
from Data.NodeDatabaseManagement import NodeDatabaseManagement
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
    node_db = NodeDatabaseManagement()
    return fetch_entity(node_db.list_categories(), "categories")


@categories_bp.route('/categories_with_files', methods=['GET'])
@login_required
def list_categories_with_files():
    """ List all categories the user has with files.

    :return: A JSON response containing the list of categories with files.
    :raises: JSON response with error message on failure.
    """
    node_db = NodeDatabaseManagement()
    return fetch_entity(node_db.list_categories_with_files(), "categories")
