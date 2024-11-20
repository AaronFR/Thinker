import logging

from flask import Blueprint, jsonify, request

from Data.Configuration import Configuration
from Utilities.auth_utils import login_required

config_bp = Blueprint('config', __name__)


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
    try:
        config = Configuration.load_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    try:
        logging.info("trying to update config")
        data = request.json
        if not data:
            raise ValueError("No JSON data received")

        field = data.get('field')
        value = data.get('value')
        if not field or value is None:
            return jsonify({'error': 'Field and value are required'}), 400

        Configuration.update_config_field(field, value)
        return jsonify({"message": f"Config - {field}: {value} updated successfully"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
