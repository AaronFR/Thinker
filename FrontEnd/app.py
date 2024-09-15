"""
Flask Backend Application

This module sets up a Flask server to serve a simple development message
in JSON format through the `/api/message` endpoint.
"""

from flask import Flask, jsonify

# Instantiate the Flask application
app = Flask(__name__)

@app.route('/api/message', methods=['GET'])
def get_message():
    """
    Retrieve a simple development message.

    This endpoint returns a JSON object containing a message to inform 
    users of the current development status of the site.

    Returns:
        Response: A Flask Response object containing a JSON representation 
                   of the development message.
    """
    return jsonify({"message": "Hello, this site is in development!"})

if __name__ == '__main__':
    # Run the Flask application in debugging mode (only for development purposes)
    app.run(debug=True)