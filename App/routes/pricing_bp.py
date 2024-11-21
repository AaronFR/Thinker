import logging

from flask import Blueprint, jsonify

from Data.Pricing import Pricing
from Utilities.Routing import fetch_entity
from Utilities.auth_utils import login_required

pricing_bp = Blueprint('pricing', __name__)


@pricing_bp.route('/pricing/session', methods=['GET'])
@login_required
def get_session_cost():
    return fetch_entity(Pricing.get_session_cost(), "cost")
