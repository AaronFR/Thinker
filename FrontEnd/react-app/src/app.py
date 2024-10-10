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

    This endpoint accepts a JSON payload containing a user prompt,
    processes it, and returns a response.

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
        persona = "Coder"
        coder = Coder("Coder")
        # response_message = f"PROTO: Trying to send request : {user_prompt}"
        response_message = coder.query(user_prompt)
        logging.info(response_message)

        return jsonify({"message": response_message})
    
    except Exception as e:
        logging.exception("Failed to process message")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logging.info("Back end is running")
    # Run the Flask application in debugging mode (only for development purposes)
    app.run(debug=True)