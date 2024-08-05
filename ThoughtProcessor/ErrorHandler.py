import io
import logging
import sys


class ErrorHandler:
    """Centralized error handling class for consistent logging and exception management."""

    @staticmethod
    def setup_logging(log_file: str = 'application.log'):
        """Sets up logging configuration."""
        file_handler = logging.FileHandler(log_file, encoding='utf-8')

        # Wrap the standard output with a TextIOWrapper to set the encoding
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        stream_handler = logging.StreamHandler(sys.stdout)

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

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
    logging.info("Something please")



