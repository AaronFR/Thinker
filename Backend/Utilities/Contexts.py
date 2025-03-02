import logging

from flask import g


# Request Info

def set_streaming(streaming: bool):
    """
    Specifies if the request is a streaming request or not. Which affects how the program will send back data
    """
    g.streaming = streaming


def is_streaming():
    """
    Returns if the current request is a streamed request or regular
    """
    return getattr(g, 'streaming', False)


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


def set_category_context(category_id: str):
    """
    Set the category_id for the current Flask context, corresponds directly with the CATEGORY node in the DB.
    Necessary as the code can be faster than getting category id from the DB which causes nothing to be returned for
    new categories
    """
    g.category_context = category_id


def get_category_context():
    """
    Get the message_id from Flask's g object. Returns None if not set.
    """
    category_id = getattr(g, 'category_context', None)
    if not category_id:
        logging.error("No category id found!")

    return category_id


# Workflow step context

def set_iteration_context(iteration: int):
    """
    Set the iteration id in Flask's g object.
    """
    g.iteration_context = iteration


def get_iteration_context():
    """
    Get the iteration from Flask's g object. Returns None if not set.
    """
    return getattr(g, 'iteration_context', None)


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


# Payment


def set_earmarked_sum(earmarked_sum: float):
    """
    Specify an amount of money that is earmarked for the upcoming LLM request, this sum will have been extracted from
    the user's balance.
    """
    g.earmarked_sum = earmarked_sum


def get_earmarked_sum() -> float | None:
    """
    Return the sum currently earmarked for the current request, if no sum is currently earmarked returns a zero valued
    float.

    Zero's the earmarked sum after retrival, by design of the system no request
    """
    earmarked_sum = getattr(g, 'earmarked_sum', 0.0)
    set_earmarked_sum(0.0)
    return earmarked_sum
