"""
Flask Backend Application

This module sets up a Flask server to serve a simple development message
in JSON format through the `/api/message` endpoint.
"""
import logging
import sys
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Functionality.Augmentation import Augmentation
from Personas.Coder import Coder
from Data.Configuration import Configuration
from Data.Pricing import Pricing

logging.basicConfig(level=logging.DEBUG)

# Instantiate the Flask application
app = Flask(__name__)
CORS(app)


@app.route('/api/message', methods=['GET'])
def get_message():
    """
    Retrieve a simple development message.

    This endpoint returns a JSON object containing a message to inform 
    users of the current development status of the site.

    :returns: A Flask Response object containing a JSON representation 
              of the development message.
    """
    return jsonify({"message": "Hello, this site is in development!"})


@app.route('/api/message', methods=['POST'])
def process_message():
    """
    Accept a user prompt and process it through the selected persona.

    :returns: A Flask Response object containing a JSON representation of the processed message.
    """
    logging.info("process_message triggered")
    try:
        data = request.get_json()
        user_prompt = data.get("prompt")
        if user_prompt is None:
            return jsonify({"error": ERROR_NO_PROMPT}), 400

        selected_persona = get_selected_persona(data) 
        response_message = selected_persona.query(user_prompt)
        logging.info("Response generated: %s", response_message)

        return jsonify({"message": response_message})
    
    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to process message")
        return jsonify({"error": str(e)}), 500

def get_selected_persona(data):
    """ Determine the selected persona or default to 'coder'. """
    persona_selection = data.get("persona")
    if persona_selection == 'coder':
        persona = Coder("Coder")
    if persona_selection not in ['coder']:
        logging.warning("Invalid persona selected, defaulting to coder")
        return Coder("Default")
    return persona


@app.route('/api/augment_prompt', methods=['POST'])
def augment_user_prompt():
    """
    Accept a user prompt and augment it in line with prompt engineering standards.

    :returns: A Flask Response object containing a JSON representation of the augmented message.
    """
    logging.info("augment_user_prompt triggered")

    try:
        data = request.get_json()
        logging.info(f"Processing augmented prompt, data: {data}")

        user_prompt = data.get("user_prompt")
        if user_prompt is None:
            return jsonify({"error": "No user prompt provided"}), 400

        augmented_response = Augmentation.augment_prompt(user_prompt)
        logging.info(f"Augmented response: \n{augmented_response}")

        return jsonify({"message": augmented_response})

    except ValueError as ve:
        logging.error("Value error: %s", str(ve))
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Failed to augment message")
        return jsonify({"error": str(e)}), 500


@app.route('/data/config', methods=['GET'])
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


@app.route('/data/config', methods=['POST'])
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


@app.route('/pricing/session', methods=['GET'])
def get_session_cost():
    try:
        logging.info("Extracting current session cost")
        cost = Pricing.get_session_cost()

        return jsonify({"cost": cost}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logging.info("Back end is running")
    # Run the Flask application in debugging mode (only for development purposes)
    app.run(debug=True)
