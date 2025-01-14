import logging
import random


def generate_random_colour() -> str:
    """
    Generate a random color in HEX format.

    :return: A string representing a color in HEX format.
    """
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    logging.debug(f"Generated random color: {color}")
    return color


def is_valid_hex_color(color: str) -> bool:
    """
    Validates whether a given string is a valid HEX color code.

    :param color: The color string to validate.
    :return: True if valid, False otherwise.
    """
    if isinstance(color, str) and color.startswith("#") and len(color) == 7:
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    return False