import logging

from flask import Blueprint, jsonify, request

from Data.Pricing import Pricing
from Utilities.Routing import fetch_entity, parse_and_validate_data
from Utilities.AuthUtils import login_required

pricing_bp = Blueprint('pricing', __name__)

TOP_UP_USER_BALANCE_SCHEMA = {
    "sum": {"required": True, "type": float},
}


@pricing_bp.route('/pricing/session', methods=['GET'])
@login_required
def get_session_cost():
    return fetch_entity(Pricing.get_session_cost(), "cost")


@pricing_bp.route('/pricing/balance', methods=['GET'])
@login_required
def get_user_balance():
    return fetch_entity(Pricing.get_user_balance(), "balance")


@pricing_bp.route('/pricing/add', methods=['POST'])
@login_required
def add_to_user_balance():
    """Add an amount to the user's balance.

    This function processes the request to top up the user's balance by checking
    if the amount provided is a float and then updating the balance accordingly.
    """
    logging.info("Attempting to top up user balance")
    data = request.json
    parsed_data = parse_and_validate_data(data, TOP_UP_USER_BALANCE_SCHEMA)

    sum = parsed_data.get('sum')

    if sum <= 0:
        logging.warning(f"Attempting to add a non-positive sum: {sum}. Only positive values are typically expected.")
        return jsonify({"error": "The sum must be a positive float for this operation."}), 400

    response = Pricing.top_up_user_balance(sum)
    if response.get("status_code") == 500:
        return jsonify({"error": "Internal database error."}), 500

    return fetch_entity(f"User balance topped up by {sum}", "message")
