import codecs
import logging
import os
import sys


class ErrorHandler:
    """Centralized error handling class for consistent logging and exception management.
    ToDo: Currently has to be initialised in every class for logs to *actually* be logged, which can easily lead to
    mistakes
    """

    @staticmethod
    def setup_logging(log_file: str = 'application.log', logger_name: str = None, format_scheme: str = '%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s'):
        """Sets up logging configuration."""
        thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")
        os.makedirs(thoughts_folder, exist_ok=True)

        log_file_location = os.path.join(thoughts_folder, log_file)
        if logger_name:
            logger = logging.getLogger(logger_name)
        else:
            logger = logging.getLogger()  # get base logger

        # Clear any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file_location, encoding='utf-8')
        console_handler = logging.StreamHandler(codecs.getwriter('utf-8')(sys.stdout.buffer))

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


    logging.debug("Anything?")
    logging.info("Something please")
    logging.info("Ł, written without crashing")

