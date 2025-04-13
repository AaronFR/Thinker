from flask import Blueprint, request

from App import limiter
from App.extensions import user_key_func
from Constants.Constants import LIGHTLY_RESTRICTED, USER_LIGHTLY_RESTRICTED
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Utilities.Routing import fetch_entity, parse_and_validate_data
from Utilities.Decorators.AuthorisationDecorators import login_required

categories_bp = Blueprint('categories', __name__)


UPDATE_CATEGORY_INSTRUCTIONS_SCHEMA = {
    "category_name": {"required": True, "type": str},
    "new_category_instructions": {"required": True, "type": str}
}


MAX_FIELD_SIZE = 50000


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


@categories_bp.route('/categories_with_messages', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def list_categories_with_messages():
    """ List all categories the user has with messages.

    :return: A JSON response containing the list of categories with files.
    :raises: JSON response with error message on failure.
    """
    return fetch_entity(nodeDB().list_categories_with_messages(), "categories")


@categories_bp.route('/categories_with_files', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def list_categories_with_files():
    """ List all categories the user has with files.

    :return: A JSON response containing the list of categories with files.
    :raises: JSON response with error message on failure.
    """
    return fetch_entity(nodeDB().list_categories_with_files(), "categories")


@categories_bp.route('/category_instructions', methods=['POST'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def update_category_instructions():
    """ Update the category instructions used as a system message for the given category

    category_name is case-insensitive, will be lowercase-d for request.
    new_category_instruction is capped at 50k characters because come-on.

    :return: A JSON response indicating success or failure to update the category's instructions
    """
    data = request.get_json()
    parsed_data = parse_and_validate_data(data, UPDATE_CATEGORY_INSTRUCTIONS_SCHEMA)
    category_name = parsed_data.get("category_name").lower()
    new_category_instructions = parsed_data.get("new_category_instructions")[:MAX_FIELD_SIZE]

    updated_category_instructions = nodeDB().update_category_instructions(category_name, new_category_instructions)

    return fetch_entity(bool(updated_category_instructions), "instructions_updated")
