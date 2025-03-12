import functools
import logging
from functools import wraps

from flask import request, jsonify

from Constants.Exceptions import failed_to_retrieve_user_balance
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Data.Pricing import Pricing
from Utilities.Encryption import decode_jwt
from Utilities.Contexts import set_user_context


def evaluate_gemini_balance():
    """
    Determines if the current system gemini balance is still positive, this is one layer in mitigating malicious attacks

    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                if NodeDB().get_system_gemini_balance() <= 0:
                    raise Exception("System cannot afford call")
            except Exception:
                logging.exception("System cannot make Gemini Calls!")
                return "SYSTEM ERROR : INCAPABLE OF MAKING GEMINI REQUESTS"

            result = method(*args, **kwargs)
            return result
        return wrapper
    return decorator


ACCESS_TOKEN_COOKIE = 'access_token_cookie'


def balance_required(fn):
    """
    Decorator to ensure that the user has a sufficient balance to perform a transaction.

    :param fn: The function to decorate.
    :return: The wrapped function with balance check.
    """
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

        # Retrieve and validate user balance
        try:
            balance = Pricing.get_user_balance()
        except Exception:
            logging.exception(failed_to_retrieve_user_balance(user_id))
            return jsonify({"status": "error", "error": "Unable to retrieve balance"}), 500

        if not (isinstance(balance, float) or isinstance(balance, int)):
            logging.warning(f"Invalid balance type for user_id {user_id}: {type(balance).__name__}")
            return jsonify({"status": "invalid", "error": "Invalid balance format"}), 400

        if balance <= 0.0:
            logging.info(f"User_id {user_id} has insufficient balance: {balance}")
            return jsonify({"status": "forbidden", "error": "Insufficient balance"}), 403

        logging.debug(f"User_id {user_id} has sufficient balance: {balance}")

        # Proceed with the request
        return fn(*args, **kwargs)

    return wrapper
