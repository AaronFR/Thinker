import logging

from flask import Blueprint, jsonify

from Data.Pricing import Pricing
from Utilities.auth_utils import login_required

pricing_bp = Blueprint('pricing', __name__)


@pricing_bp.route('/pricing/session', methods=['GET'])
@login_required
def get_session_cost():
    try:
        logging.info("Extracting current session cost")
        cost = Pricing.get_session_cost()

        return jsonify({"cost": cost}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
