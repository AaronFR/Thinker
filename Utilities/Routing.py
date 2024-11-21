import logging
from flask import request, jsonify


def fetch_entity(entity, entity_name=None, success_status=200):
    """

    :param entity: the result to return to the client
    :param entity_name: Included if the result is to be labeled inside a JSON object, not included if the response is
     itself a JSON object to be sent over as is
    :param success_status: success status code, typically 200
    :return: The json response with status, e.g { "entity_name": "entity_result" }, 200
    """
    try:
        if entity_name:
            return jsonify({entity_name: entity}), success_status
        else:
            return jsonify(entity), success_status
    except Exception as e:
        return handle_error(e)


def handle_error(e):
    """
    Centralized error handler that logs the failing method and route and returns a JSON error response.
    """
    route = request.path
    method = request.method
    logging.error(f"Error in {route} {method}: {e}")
    return jsonify({"error": str(e)}), 500
