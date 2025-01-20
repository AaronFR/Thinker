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
        logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()

        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(logging.DEBUG)

        # Set up file handler
        if os.getenv("STORAGE_TYPE") == "local":
            file_handler = ErrorHandler.setup_file_handler(log_file, format_scheme)
            if file_handler:
                file_handler.setLevel(logging.DEBUG)
                logger.addHandler(file_handler)

        # Set up console handler
        console_handler = logging.StreamHandler(codecs.getwriter(Constants.DEFAULT_ENCODING)(sys.stdout.buffer))
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(format_scheme)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    @staticmethod
    def setup_file_handler(log_file: str, format_scheme: str):
        """
        Sets up the file handler for logging, including creating the logs directory.
        Only to be used when run locally

        :param log_file: The name of the log file to be created or overwritten.
        :param format_scheme: The formatting scheme for log messages.
        :return: Configured FileHandler or None if setup fails.
        """
        try:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            logs_directory = os.path.join(script_directory, '../../UserData', 'Logs')

            os.makedirs(logs_directory, exist_ok=True)
            logging.debug(f"Logs directory ensured at: {logs_directory}")

            log_file_location = os.path.join(logs_directory, log_file)
            logging.debug(f"Log file location set to: {log_file_location}")

            file_handler = logging.FileHandler(log_file_location, encoding=Constants.DEFAULT_ENCODING)
            formatter = logging.Formatter(format_scheme)
            file_handler.setFormatter(formatter)

            logging.debug("File handler successfully created.")
            return file_handler

        except Exception as e:
            logging.error(f"Failed to create file handler: {e}")
            return None


if __name__ == '__main__':
    ErrorHandler.setup_logging()

    logging.debug("Debug log initialized.")
    logging.info("Info log initialized.")
    logging.info("Ç, written without crashing")
