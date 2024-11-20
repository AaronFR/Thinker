import logging

import shortuuid
from flask import Blueprint
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Utilities.UserContext import set_user_context
import time

from App import jwt
from Utilities.Encryption import hash_password, check_password

from flask import jsonify, request, make_response
from flask_jwt_extended import create_access_token, decode_token, unset_jwt_cookies, create_refresh_token

from Utilities.auth_utils import decode_jwt

authorisation_bp = Blueprint('auth', __name__)

ERROR_NO_ID = "No user id found"
ACCESS_TOKEN_COOKIE = "access_token_cookie"
REFRESH_TOKEN_COOKIE = "refresh_token"
BLACKLIST = set()  # ToDo: Will need to be more robust


@authorisation_bp.route('/register', methods=['POST'])
def register():
    """
    ToDo: Add in user warnings or at least logging if a method fails to find a user in the db, failing a query

    :return: a valid response including access and refresh JWT cookies
    """
    data = request.json

    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    password_hash = hash_password(data.get('password'))
    if not data.get('password'):
        return jsonify({"error": "Password is required"}), 400

    node_db = NodeDatabaseManagement()
    user_id = str(shortuuid.uuid())

    if node_db.user_exists(email):
        logging.warning(f"Registration failed: User with email {email} already exists.")
        return jsonify({"error": "User with this email already exists"}), 409

    logging.info("Registering new user")
    registered = node_db.create_user(user_id, email, password_hash)
    if registered:
        logging.info("Successfully registered new user")
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        response = make_response(jsonify({"message": "User registration successful"}))
        response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, httponly=True, secure=True)
        response.set_cookie(REFRESH_TOKEN_COOKIE, refresh_token, httponly=True, secure=True, samesite="Strict")
        return response
    else:
        logging.error("Failed to register new user!")
        return jsonify({"Failure": "Failed to register user"}), 500


@authorisation_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    node_db = NodeDatabaseManagement()
    user_id = node_db.find_user_by_email(email)
    if not user_id:
        return jsonify({"error": "This email is not present in our systems"}), 400

    password = data.get("password")
    if not password:
        return jsonify({"error": "Password is required"}), 400
    password_hash = node_db.get_user_password_hash(user_id)
    if not check_password(password, password_hash):
        return jsonify({"error": "Incorrect password"}), 400

    try:
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie(ACCESS_TOKEN_COOKIE, access_token, httponly=True, secure=True)
        response.set_cookie(REFRESH_TOKEN_COOKIE, refresh_token, httponly=True, secure=True, samesite="Strict")
        return response
    except Exception as e:
        logging.exception("Failed to login")
        return jsonify({"error": "Failed to login"}), 401


@authorisation_bp.route('/auth/validate', methods=['GET'])
def validate_session():
    try:
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            logging.info("No access_token cookie found")
            return jsonify({"status": "invalid", "error": "No token provided"}), 401

        user_id = decode_jwt(token)
        if not user_id:
            return jsonify({"status": "invalid", "error": "Invalid token"}), 401
        set_user_context(user_id)

        logging.debug(f"Decoded user_id: {user_id}")
        return jsonify({"status": "valid", "user_id": user_id}), 200
    except Exception as e:
        logging.exception("Error validating token")
        return jsonify({"status": "invalid", "error": "Unexpected error"}), 500


@authorisation_bp.route('/logout', methods=['POST'])
def logout():
    try:
        logging.info("Validating JWT for logout")
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            logging.info("No access_token cookie found")
            return jsonify({"status": "invalid", "error": "No token provided"}), 401
    except Exception as e:
        logging.exception("JWT validation failed")
        return jsonify({"error": "JWT validation failed"}), 401

    response = make_response(jsonify({"message": "Successfully logged out"}))
    unset_jwt_cookies(response)
    return response


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST


@authorisation_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token missing"}), 401

    try:
        # Validate and decode the refresh token
        decoded_token = decode_token(refresh_token)
        user_id = decoded_token["sub"]

        # Check for token expiration (optional, depending on decode_token implementation)
        if "exp" in decoded_token and decoded_token["exp"] < time.time():
            return jsonify({"error": "Refresh token expired"}), 401

        new_access_token = create_access_token(identity=user_id)
        new_refresh_token = create_refresh_token(identity=user_id)

        response = make_response(jsonify({
            "message": "Token refreshed",
            ACCESS_TOKEN_COOKIE: new_access_token
        }))
        response.set_cookie(ACCESS_TOKEN_COOKIE, new_access_token, httponly=True, secure=True)
        response.set_cookie(REFRESH_TOKEN_COOKIE, new_refresh_token, httponly=True, secure=True, samesite="Strict")
        return response

    except Exception as e:
        logging.error(f"Refresh token error: {e}")
        return jsonify({"error": "Invalid refresh token"}), 401
