import functools
import logging

from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities.Contexts import get_functionality_context, set_functionality_context


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
