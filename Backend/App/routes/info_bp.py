import logging

from flask import Blueprint, request, jsonify
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB

info_bp = Blueprint('info', __name__)


@info_bp.route('/info/user', methods=['POST'])
def get_user_info():
    """
    Endpoint to fetch user information based on provided parameters.

    Expects a JSON body with a 'parameters' list.
    """
    try:
        data = request.get_json()
        if not data or 'parameters' not in data:
            return jsonify({"error": "Missing 'parameters' in request body."}), 400

        parameters = data.get('parameters')

        if not isinstance(parameters, list):
            return jsonify({"error": "'parameters' should be a list."}), 400

        parameters = [param.strip() for param in parameters if param.strip()]

        if not parameters:
            return jsonify({"error": "No valid parameters provided."}), 400

        user_info = NodeDB().get_user_information(parameters)

        return jsonify({"user_data": user_info}), 200

    except Exception as e:
        logging.exception("Failed to fetch user information.")
        return jsonify({"error": str(e)}), 500
