import logging
import os
from functools import wraps

import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import abort

from Constants.Constants import REDISCLOUD_URL, LIGHTLY_RESTRICTED, \
    LIGHTLY_RESTRICTED_HIGH_FREQUENCY
from Utilities.Contexts import get_user_context

redis_url = os.environ.get(REDISCLOUD_URL, None)

# Initialize Redis based on whether REDISCLOUD_URL is available
r = None
if redis_url:
    try:
        r = redis.from_url(redis_url)
        # Test the connection
        r.ping()
        print("Redis connected using URL.")
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis using URL: {e}. Falling back to localhost.")
        r = redis.Redis(host='localhost', port=6379, db=0)
else:
    print("Redis connected to localhost.")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[LIGHTLY_RESTRICTED, LIGHTLY_RESTRICTED_HIGH_FREQUENCY],
    storage_uri=redis_url
)


def socket_rate_limit(key_func, limit: int, period: int):
    """
    A decorator to rate limit a SocketIO event handler.

    :param key_func: A function that returns a unique key for rate limiting (e.g., based on user session).
    :param limit: The maximum allowed calls in the given period.
    :param period: The period (in seconds) over which the limit applies.
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if redis_url:
                key = key_func(*args, **kwargs)
                try:
                    current_count = r.incr(key)
                    if current_count == 1:
                        # When first request, set the expiration.
                        r.expire(key, period)
                    elif current_count > limit:
                        # When limit exceeded, log or notify the user.
                        logging.warning(f"Rate limit exceeded for key: {key}")
                        # ToDo: emit an error event back to the client
                        abort(500)
                    return f(*args, **kwargs)
                except redis.exceptions.ConnectionError as e:
                    logging.error(f"Redis connection error: {e}")
                    abort(500)
            else:
                # limiter is not enabled in dev env
                return f(*args, **kwargs)

        return wrapped

    return decorator


def system_key_func(*args, **kwargs):
    """
    Anonymous, assigning this key means it applies to everyone, at a system level
    """
    return "socketio_rate:anonymous"


def user_key_func(*args, **kwargs):
    """
    ToDo: The current user_key_func could be highly annoying to those on VPNs, trying to login and register -
     we can't use their user id before they do
    """
    user_id = get_user_context()
    if user_id is not None:
        return f"user_rate:{user_id}"

    # Fallback to IP-based rate limiting if no user is found.
    return get_remote_address()
