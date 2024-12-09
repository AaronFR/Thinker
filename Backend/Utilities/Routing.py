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


def parse_and_validate_data(data, schema):
    """
    Generalized function to parse and validate data against a defined schema.

    :param data: The incoming WebSocket data (dictionary).
    :param schema: A dictionary defining required fields, their default values, and validation rules.
                   Example:
                   {
                       "prompt": {"required": True},
                       "additionalQA": {"required": False, "default": None},
                       "tags": {"required": False, "default": {}, "type": dict},
                       "files": {"required": False, "default": [], "type": list},
                   }
    :return is_websocket: changes the function to emit "error" events for websockets
    :return: A dictionary of validated and parsed values.
    :raises ValueError: If a required field is missing or validation fails.
    """
    parsed_data = {}

    for key, rules in schema.items():
        if key in data:
            value = data[key]
            # Validate type if specified
            if "type" in rules and not isinstance(value, rules["type"]):
                raise ValueError(f"Field '{key}' must be of type {rules['type'].__name__}.")
            parsed_data[key] = value
        elif rules.get("required", False):
            raise ValueError(f"Missing required field: '{key}'.")
        else:
            # Use default value if the field is optional
            parsed_data[key] = rules.get("default")

    return parsed_data


def handle_error(e):
    """
    Centralized error handler that logs the failing method and route and returns a JSON error response.
    """
    route = request.path
    method = request.method
    logging.error(f"Error in {route} {method}: {e}")
    return jsonify({"error": str(e)}), 500
