import logging
import os
from functools import wraps

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from Constants.Constants import REDISCLOUD_URL, LIGHTLY_RESTRICTED, \
    LIGHTLY_RESTRICTED_HIGH_FREQUENCY

redis_url = os.environ.get(REDISCLOUD_URL, None)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[LIGHTLY_RESTRICTED, LIGHTLY_RESTRICTED_HIGH_FREQUENCY],
    storage_uri=redis_url
)

