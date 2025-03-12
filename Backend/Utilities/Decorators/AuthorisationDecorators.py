import logging

from functools import wraps
from flask import request, jsonify
from flask_socketio import emit, disconnect

from Utilities.Contexts import set_user_context
from Utilities.Encryption import decode_jwt

ACCESS_TOKEN_COOKIE = "access_token_cookie"
REFRESH_TOKEN_COOKIE = "refresh_token_cookie"


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Retrieve the JWT from the cookies
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            logging.info("No access_token cookie found")
            return jsonify({"status": "invalid", "error": "No token provided"}), 401

        user_id = decode_jwt(token)
        if not user_id:
            return jsonify({"status": "invalid", "error": "Invalid token"}), 401
        set_user_context(user_id)

        logging.debug(f"Decoded user_id: {user_id}")

        # Proceed with the request
        return fn(*args, **kwargs)

    return wrapper


def login_required_ws(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Retrieve the JWT from the cookies
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            emit('error', {'error': 'token_missing'})
            disconnect()
            return

        user_id = decode_jwt(token, is_websocket=True)
        if not user_id:
            return jsonify({"status": "invalid", "error": "Invalid token"}), 401
        set_user_context(user_id)

        logging.debug(f"Decoded user_id: {user_id}")

        # Proceed with the request
        return fn(*args, **kwargs)

    return wrapper


