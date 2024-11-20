import logging
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import decode_token

from Utilities.UserContext import set_user_context

ACCESS_TOKEN_COOKIE = "access_token_cookie"
REFRESH_TOKEN_COOKIE = "refresh_token"


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


def decode_jwt(token):
    """
    Decode and validate the JWT token.
    """
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")  # 'sub' is typically used for user_id
        return user_id
    except Exception as e:
        logging.error(f"JWT validation error: {e}")
        return None