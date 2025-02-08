import logging

from flask import Blueprint, request, jsonify

from Data.Configuration import Configuration
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities.AuthUtils import login_required
from Utilities.Routing import fetch_entity, parse_and_validate_data

info_bp = Blueprint('info', __name__, url_prefix='/info')

UPDATE_CONFIG_SCHEMA = {
    "field": {"required": True, "type": str},
    "value": {"required": True, "type": object},
}


@info_bp.route('/user', methods=['POST'])
@login_required
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


@info_bp.route('/config', methods=['GET'])
@login_required
def load_config():
    """
    Load the configuration from the YAML file and return it as a JSON response.

    This endpoint retrieves the entire application configuration, stored in
    a YAML file, and returns it as a JSON object. This is useful for reading
    the current settings, such as dark mode preferences, without modifying
    the configuration.

    :returns: JSON response containing the configuration dictionary.
    """
    return fetch_entity(Configuration.load_config())


@info_bp.route('/config', methods=['POST'])
@login_required
def update_config():
    """
    Load the configuration from the YAML file and return it as a JSON response.

    This endpoint retrieves the entire application configuration, stored in
    a YAML file, and returns it as a JSON object. This is useful for reading
    the current settings, such as dark mode preferences, without modifying
    the configuration.

    :returns: JSON response containing the configuration dictionary.
    """
    logging.info("trying to update config")
    data = request.json
    parsed_data = parse_and_validate_data(data, UPDATE_CONFIG_SCHEMA)
    field = parsed_data.get('field')
    value = parsed_data.get('value')

    Configuration.update_config_field(field, value)
    return fetch_entity(f"Config - {field}: {value} updated successfully", "message")