from flask import g
from typing import List


# User Request Info

def set_user_context(user_id: str):
    """
    Set the user_id in Flask's g object.
    """
    g.user_context = user_id


def get_user_context() -> str | None:
    """
    Get the user_id from Flask's g object. Returns None if not set.
    """
    return getattr(g, 'user_context', None)


def set_message_context(message_id: str):
    """
    Set the message_id for the current Flask context, corresponds directly with the USER_PROMPT node in the DB.
    """
    g.message_context = message_id


def get_message_context() -> str | None:
    """
    Get the message_id from Flask's g object. Returns None if not set.
    """
    return getattr(g, 'message_context', None)


# Functionalities


def set_functionality_context(function_name: str):
    """
    The specific functionality being used, primarily used for cost estimating purposes.
    """
    g.functionality_context = function_name


def get_functionality_context() -> str | None:
    """
    Get the name of the current employed functionality from Flask's g object. Returns None if not set.
    """
    return getattr(g, 'functionality_context', None)
