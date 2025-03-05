import functools
import logging

from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB


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
