import functools
import logging
from typing import Union, Callable


def handle_errors(debug_logging: bool = False, raise_errors: bool = False):
    """
    Handles any given error that occurs in the decorated function.
    Just because you can use this decorator to automatically handle errors doesn't mean you should, avoid if:
    - using this decorator makes the failing line of code harder to observe
    - complicated functionality is triggered by an error

    :param debug_logging: whether the decorated function and its arguments should be logged before and after execution
    :param raise_errors: If false the error will merely be logged, for graceful error handling. True will raise an
     error
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                if debug_logging:
                    logging.debug(f"Executing {method.__name__} with args={args}, kwargs={kwargs}")
                    result = method(*args, **kwargs)
                    logging.debug(f"{method.__name__} executed successfully, outputting: {result}")
                    return result

                return method(*args, **kwargs)
            except Exception as e:
                logging.exception(f"Error in {method.__name__}: {e}", exc_info=e)
                if raise_errors:
                    raise
        return wrapper
    return decorator


def return_for_error(return_object: Union[object, Callable], debug_logging: bool = False):
    """
    Returns a specified object if an error is encountered

    :param return_object: A static object to return in case of any general error, or a dynamic function for use in
     extracting specific parts of the user message for example
    :param debug_logging: whether the decorated function and its arguments should be logged before and after execution
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                if debug_logging:
                    logging.debug(f"Executing {method.__name__} with args={args}, kwargs={kwargs}")
                    result = method(*args, **kwargs)
                    logging.debug(f"{method.__name__} executed successfully, outputting: {result}")
                    return result

                return method(*args, **kwargs)
            except Exception as e:
                logging.exception(f"Error in {method.__name__}: {e}", exc_info=e)
                if callable(return_object):
                    return return_object(e)
                return return_object
        return wrapper
    return decorator
