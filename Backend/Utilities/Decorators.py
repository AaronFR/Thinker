import functools
import logging
from typing import Union, Callable

from Constants.Exceptions import error_in_function
from Utilities.Contexts import set_functionality_context, get_functionality_context
from Utilities.ErrorHandler import ErrorHandler

ErrorHandler.setup_logging()


def handle_errors(func=None, *, debug_logging: bool = False, raise_errors: bool = False):
    """
    Handles any errors that occur in the decorated function.

    Usage caution: This decorator may obscure the source of errors. Avoid using it if:
    - It complicates identifying the failing line of code.
    - The functionality triggered by an error is complex.

    :param func: The function being decorated
    :param debug_logging: Whether to log the function and its arguments before and after execution.
    :param raise_errors: If false the error will merely be logged, for graceful error handling. True will raise an
     error
    """
    if func is None:
        return lambda f: handle_errors(f, debug_logging=debug_logging, raise_errors=raise_errors)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if debug_logging:
                logging.debug(f"Executing {func.__name__} with args={args}, kwargs={kwargs}")

            result = func(*args, **kwargs)

            if debug_logging:
                logging.debug(f"{func.__name__} executed successfully, outputting: {result}")

            return result
        except Exception as e:
            logging.exception(error_in_function(func.__name__, e), exc_info=e)
            if raise_errors:
                raise

    return wrapper


def return_for_error(return_object: Union[object, Callable], debug_logging: bool = False):
    """
    Returns a specified object if an error is encountered

    :param return_object: A static object to return in case of a general error,
                          or a callable for extracting specific parts of the error message.
    :param debug_logging: Whether the decorated function and its arguments should be logged; before and after execution
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                if debug_logging:
                    logging.debug(f"Executing {method.__name__} with args={args}, kwargs={kwargs}")

                result = method(*args, **kwargs)

                if debug_logging:
                    logging.debug(f"{method.__name__} executed successfully, outputting: {result}")

                return result
            except Exception as e:
                logging.exception(error_in_function(method.__name__, e), exc_info=e)
                if callable(return_object):
                    return return_object(e)
                return return_object
        return wrapper
    return decorator


def specify_functionality_context(function_name: str):
    """
    Sets a specific functionality context for the duration of the method call and no longer

    :param function_name: The functionality to enable and then disable for the duration of the method
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            prior_functionality_context = get_functionality_context()
            set_functionality_context(function_name)

            result = method(*args, **kwargs)

            set_functionality_context(prior_functionality_context)
            return result
        return wrapper
    return decorator
