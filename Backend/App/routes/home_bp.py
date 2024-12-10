from flask import Blueprint

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    """
    Home page route.

    Returns:
        str: A greeting message.
    """
    return "I'm probably going to write some docs here! <i>Maybe!</i>"
