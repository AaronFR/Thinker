from contextvars import ContextVar
from typing import List

# Define global ContextVars
user_context = ContextVar("user_context", default=None)
message_context = ContextVar("message_context", default=None)
functionality_context = ContextVar("functionality_context", default=None)
expensed_nodes = ContextVar("expensed_nodes", default=[])


def set_user_context(user_id):
    """
    Set the user_id in a ContextVar.
    """
    user_context.set(user_id)


def get_user_context() -> str | None:
    """
    Get the user_id from the ContextVar. Returns None if not set.
    """
    return user_context.get()


def set_message_context(message_id):
    """
    Set the message_id for the current flask context, corresponds directly with the USER_PROMPT node in the DB
    """
    message_context.set(message_id)


def get_message_context() -> str | None:
    """
    Get the message_id from the ContextVar. Returns None if not set.
    """
    return message_context.get()


def set_functionality_context(function_name):
    """
    The specific functionality being used, primarily used for cost estimating purposes
    """
    functionality_context.set(function_name)


def get_functionality_context():
    """
    Get the name of the current employed functionality from the ContextVar. Returns None if not set.
    """
    return functionality_context.get()


def add_to_expensed_nodes(expensed_node_uuid):
    """
    Append a Node UUID to the list of expensed_nodes that will be expensed at the end of the transaction
    """
    current_list = expensed_nodes.get()
    current_list.append(expensed_node_uuid)
    expensed_nodes.set(current_list)


def set_expensed_nodes(new_list: List[str]):
    """
    re-set the entire list of Node UUID's e.g. for wiping
    """
    expensed_nodes.set(new_list)


def get_expensed_nodes() -> List[str]:
    """
    Return the list of nodes to expense by their UUID. Returns an empty list if not set.
    """
    return expensed_nodes.get()
