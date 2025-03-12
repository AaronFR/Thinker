import logging

from flask import Blueprint

from App import limiter
from Constants.Constants import LIGHTLY_RESTRICTED
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Utilities.Routing import fetch_entity
from Utilities.Decorators.AuthorisationDecorators import login_required

messages_bp = Blueprint('messages_bp', __name__, url_prefix='/messages')


@messages_bp.route('/<category_name>', methods=['GET'])
@login_required
@limiter.limit(LIGHTLY_RESTRICTED)
def get_messages(category_name):
    category_name = category_name\
        .lower()\
        .replace(' ', '_')

    return fetch_entity(nodeDB().get_messages_by_category(category_name), "messages")


@messages_bp.route('/<message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    nodeDB().delete_message_by_id(message_id)

    logging.info(f"User prompt node {message_id} deleted")
    return fetch_entity(f"Message {message_id} deleted successfully", "message")
