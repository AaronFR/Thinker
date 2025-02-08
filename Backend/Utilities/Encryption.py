import logging

import bcrypt

from Constants.Constants import DEFAULT_ENCODING


def hash_password(password):
    """
    Hashes the given password using bcrypt.

    :param password: The password to be hashed.
    :return: The hashed password.
    :raises ValueError: If the password is empty.
    """
    if not password:
        raise ValueError("Password must not be empty.")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(DEFAULT_ENCODING), salt)
    return hashed_password.decode(DEFAULT_ENCODING)


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(DEFAULT_ENCODING), hashed_password.encode(DEFAULT_ENCODING))
