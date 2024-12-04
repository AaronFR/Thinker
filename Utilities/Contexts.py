from contextvars import ContextVar

# Define global ContextVars
user_context = ContextVar("user_context", default=None)
message_context = ContextVar("message_context", default=None)


def set_user_context(user_id):
    """
    Set the user_id in a ContextVar.
    """
    user_context.set(user_id)


def get_user_context():
    """
    Get the user_id from the ContextVar. Returns None if not set.
    """
    return user_context.get()


def set_message_context(message_id):
    """
    Set the message_id in a ContextVar.
    """
    message_context.set(message_id)


def get_message_context():
    """
    Get the message_id from the ContextVar. Returns None if not set.
    """
    return message_context.get()
