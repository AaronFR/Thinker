import functools
import logging
import types
from typing import Union, Callable

from flask_socketio import emit

from Constants.Exceptions import error_in_function
from Utilities.Contexts import set_iteration_context, get_functionality_context, set_functionality_context
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


def workflow_step_handler(func):
    """
    Decorator for step methods to automatically emit start/complete events, and handle errors.
    It assumes that an 'iteration' argument is provided either as the first positional argument
    or via keyword arguments.

    Be careful adding any yields or other generators to a step, this can trigger the if iterator flow -even if the
    iterator isn't a streamed response.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Retrieve iteration from kwargs or first positional parameter.
        iteration = kwargs.get('iteration')
        if iteration is None and args:
            iteration = args[0]
        if iteration is None:
            raise ValueError("The 'iteration' parameter must be provided.")

        _emit_step_started_events(iteration)

        try:
            result = func(*args, **kwargs)

            # Determine if this step uses streaming (defaulting to False)
            streaming = kwargs.get('streaming', False)

            # For steps that return generators, you might need custom handling.
            # Here, if the result is a generator, we wrap its iteration to ensure complete event is called at the end.
            if isinstance(result, types.GeneratorType):
                emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "streaming"})

                def generator_wrapper():
                    try:
                        for item in result:
                            yield item  # Use "yield from" for transparent streaming.
                    finally:
                        _emit_step_completed_events(iteration, streaming, response="")

                return generator_wrapper()

            # For non-generator steps, emit completion after function returns.
            _emit_step_completed_events(iteration, streaming, response=str(result))
            return result

        except Exception as e:
            # Log the error and emit an error event.
            logging.exception(f"Error in step {iteration}: {e}")
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "error", "error": str(e)})

    return wrapper


UPDATE_WORKFLOW_STEP = "update_workflow_step"


def _emit_step_started_events(iteration: int):
    emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
    set_iteration_context(iteration)


def _emit_step_completed_events(iteration: int, streaming: bool, response: str):
    emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})

    if not streaming:
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "response": response})


def specify_functionality_context(function_name: str):
    """
    Sets a specific functionality context for the duration of the method call and no longer

    ToDo: There may be an issue where this decorator or others 'absorbs' the logs of the functions they run

    :param function_name: The functionality to enable and then disable for the duration of the method
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            prior_functionality_context = get_functionality_context()
            set_functionality_context(function_name)

            result = method(*args, **kwargs)

            if not isinstance(result, types.GeneratorType):
                # Otherwise a generator is defined, ready to go and instantly the functionality context will be wiped
                set_functionality_context(prior_functionality_context)

            return result
        return wrapper
    return decorator
