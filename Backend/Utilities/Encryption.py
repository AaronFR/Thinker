import bcrypt

from Utilities.Constants import DEFAULT_ENCODING


def hash_password(password):
    """

    :param password: The password to be hashed
    :return:
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(DEFAULT_ENCODING), salt)
    return hashed_password.decode(DEFAULT_ENCODING)


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(DEFAULT_ENCODING), hashed_password.encode(DEFAULT_ENCODING))
