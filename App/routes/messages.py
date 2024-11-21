import logging

from flask import Blueprint, jsonify
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Utilities.Routing import fetch_entity
from Utilities.auth_utils import login_required

messages_bp = Blueprint('messages_bp', __name__)


@messages_bp.route('/messages/<category_name>', methods=['GET'])
@login_required
def get_messages(category_name):
    category_name = category_name.lower()
    node_db = NodeDatabaseManagement()
    return fetch_entity(node_db.get_messages_by_category(category_name), "messages")


@messages_bp.route('/messages/<message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    node_db = NodeDatabaseManagement()
    node_db.delete_message_by_id(message_id)

    logging.info(f"User prompt node {message_id} deleted")
    return fetch_entity(f"Message {message_id} deleted successfully", "message")
