import logging

from flask import Blueprint, jsonify, request

from Data.Configuration import Configuration
from Utilities.Routing import fetch_entity, parse_and_validate_data
from Utilities.AuthUtils import login_required

config_bp = Blueprint('config', __name__)

UPDATE_CONFIG_SCHEMA = {
    "field": {"required": True, "type": str},
    "value": {"required": True, "type": object},
}


@config_bp.route('/data/config', methods=['GET'])
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


@config_bp.route('/data/config', methods=['POST'])
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
