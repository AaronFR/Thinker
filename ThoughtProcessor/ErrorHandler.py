import io
import logging
import os


class ErrorHandler:
    """Centralized error handling class for consistent logging and exception management."""

    @staticmethod
    def setup_logging(log_file: str = 'application.log'):
        """Sets up logging configuration."""
        thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")

        log_file_location = os.path.join(thoughts_folder, log_file)
        logger = logging.getLogger()

        # Clear any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Set the logging level
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file_location)
        console_handler = logging.StreamHandler()

        # Set level for handlers
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    @staticmethod
    def log_error(message: str, exception: Exception):
        """Logs an error message along with exception details."""
        logging.error(f"{message}: {str(exception)}")

    @staticmethod
    def handle_exception(exception: Exception, custom_message: str = "An error occurred"):
        """Handles an exception by logging the details."""
        ErrorHandler.log_error(custom_message, exception)



if __name__ == '__main__':
    ErrorHandler.setup_logging()


    logging.debug("Anything?")
    logging.info("Something please")

