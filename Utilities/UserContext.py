from contextvars import ContextVar

# Define a global ContextVar for user context
user_context = ContextVar("user_context", default=None)


def set_user_context(user_id):
    """
    Set the user_id in the ContextVar.
    """
    user_context.set(user_id)


def get_user_context():
    """
    Get the user_id from the ContextVar. Returns None if not set.
    """
    return user_context.get()
