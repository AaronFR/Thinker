from flask import Blueprint

from App import limiter
from App.extensions import user_key_func
from Constants.Constants import USER_LIGHTLY_RESTRICTED

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@limiter.limit(USER_LIGHTLY_RESTRICTED, key_func=user_key_func)
def home():
    """
    Home page route.

    Returns:
        str: A greeting message.
    """
    return "I'm probably going to write some docs here! <i>Maybe!</i>"
