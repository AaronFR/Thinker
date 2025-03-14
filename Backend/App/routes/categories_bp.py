from flask import Blueprint

from App import limiter
from App.extensions import user_key_func
from Constants.Constants import LIGHTLY_RESTRICTED, USER_LIGHTLY_RESTRICTED
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Utilities.Routing import fetch_entity
from Utilities.Decorators.AuthorisationDecorators import login_required

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/categories', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def list_categories():
    """ List all categories for the user

    :return: A JSON response containing the list of categories.
    :raises: JSON response with error message on failure.
    """
    return fetch_entity(nodeDB().list_categories(), "categories")


@categories_bp.route('/categories_with_files', methods=['GET'])
@login_required
@limiter.limit(USER_LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def list_categories_with_files():
    """ List all categories the user has with files.

    :return: A JSON response containing the list of categories with files.
    :raises: JSON response with error message on failure.
    """
    return fetch_entity(nodeDB().list_categories_with_files(), "categories")
