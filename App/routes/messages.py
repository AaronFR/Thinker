import logging

from flask import Blueprint, jsonify
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Utilities.auth_utils import login_required

messages_bp = Blueprint('messages_bp', __name__)


@messages_bp.route('/messages/<category_name>', methods=['GET'])
@login_required
def get_messages(category_name):
    try:
        category_name = category_name.lower()
        node_db = NodeDatabaseManagement()
        messages_list = node_db.get_messages_by_category(category_name)

        return jsonify({"messages": messages_list}), 200
    except Exception as e:
        logging.exception(f"Failed to get messages for category, {category_name}")
        return jsonify({"error": str(e)}), 500


@messages_bp.route('/messages/<message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    try:
        node_db = NodeDatabaseManagement()
        node_db.delete_message_by_id(message_id)

        logging.info(f"User prompt node {message_id} deleted")
        return jsonify({"message": f"Message {message_id} deleted successfully"}), 200
    except Exception as e:
        logging.exception(f"Failed to delete message {message_id}")
        return jsonify({"error": str(e)}), 500