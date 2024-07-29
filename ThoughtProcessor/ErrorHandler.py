import logging

class ErrorHandler:
    """Centralized error handling class for consistent logging and exception management."""

    @staticmethod
    def setup_logging(log_file: str = 'application.log'):
        """Sets up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
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



