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
    Accept a user prompt and process it.

    This endpoint accepts a JSON payload containing a user prompt and persona
    processes the prompt through the selected persona, returning a response.

    :returns: A Flask Response object containing a JSON representation
              of the processed message.
    """
    logging.info("proces_message triggered")

    try:
        data = request.get_json()
        logging.info(f"processing prompt, data: {data}")

        user_prompt = data.get("prompt")
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Process the prompt with the coder persona (placeholder)

        personaSelection = data.get("persona")
        if not personaSelection:
            logging.error("!!! SELECT PERSONA FUNCTIONALITY IS BROKEN")
            personaSelection = 'coder'

        if personaSelection == 'coder':
            persona = Coder("Coder")
        else:
            persona = Coder("Default")
            
        response_message = persona.query(user_prompt)
        logging.info(response_message)

        return jsonify({"message": response_message})
    
    except Exception as e:
        logging.exception("Failed to process message")
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
