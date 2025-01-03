import codecs
import logging
import os
import sys

from Utilities import Constants


class ErrorHandler:
    """Centralized error handling class for consistent logging and exception management.
    ToDo: Currently has to be initialised in every class for logs to *actually* be logged, which can easily lead to
     mistakes
    """

    @staticmethod
    def setup_logging(
            log_file: str = 'application.log',
            logger_name: str = None,
            format_scheme: str = '%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s'):
        """Sets up logging configuration.

        This method creates a logging directory if it does not exist and sets up file and console handlers
        according to the specified logging configuration.

        :param log_file: The name of the log file to be created or overwritten.
        :param logger_name: An optional name for the logger. If None, the base logger is used.
        :param format_scheme: The formatting scheme for log messages.
        """
        logs_directory = os.path.join(os.path.dirname(__file__), '../../UserData', 'Logs')
        os.makedirs(logs_directory, exist_ok=True)

        log_file_location = os.path.join(logs_directory, log_file)
        logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()

        # Clear any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(logging.DEBUG)

        # Set up file handler with defined encoding
        file_handler = logging.FileHandler(log_file_location, encoding=Constants.DEFAULT_ENCODING)
        console_handler = logging.StreamHandler(codecs.getwriter(Constants.DEFAULT_ENCODING)(sys.stdout.buffer))

        # Set level for handlers
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(format_scheme)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)


if __name__ == '__main__':
    ErrorHandler.setup_logging()

    logging.debug("Debug log initialized.")
    logging.info("Info log initialized.")
    logging.info("Ç, written without crashing")
