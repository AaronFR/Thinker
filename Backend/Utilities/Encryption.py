import logging

import bcrypt
import jwt as pyjwt
from flask_jwt_extended import decode_token
from flask_socketio import emit, disconnect

from Constants.Constants import DEFAULT_ENCODING


# Hashing & Hashed Values

def hash_password(password):
    """
    Hashes the given password using bcrypt.

    :param password: The password to be hashed.
    :return: The hashed password.
    :raises ValueError: If the password is empty.
    """
    if not password:
        raise ValueError("Password must not be empty.")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(DEFAULT_ENCODING), salt)
    return hashed_password.decode(DEFAULT_ENCODING)


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(DEFAULT_ENCODING), hashed_password.encode(DEFAULT_ENCODING))


# JWTs


def decode_jwt(token, is_websocket: bool = False):
    """
    Decode and validate the JWT token.
    """
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")  # 'sub' is typically used for user_id

        return user_id
    except pyjwt.ExpiredSignatureError:
        if is_websocket:
            emit('error', {'error': 'token_expired'})
            disconnect()

        return None
    except Exception as e:
        logging.error(f"JWT validation error: {e}")
        if is_websocket:
            emit('error', {'error': 'invalid_token'})
            disconnect()

        return None
