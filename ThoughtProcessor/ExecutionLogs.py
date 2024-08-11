import logging
from ThoughtProcessor.ErrorHandler import ErrorHandler


class ExecutionLogs:
    """
    Class for managing and writing execution logs using the centralized ErrorHandler logger.
    """

    @staticmethod
    def setup_logging():
        """Sets up the logger for execution logs using ErrorHandler."""
        ErrorHandler.setup_logging(
            log_file='execution_logs.log',
            logger_name='ExecutionLogger',
            format_scheme='%(asctime)s : %(message)s')

    @staticmethod
    def add_to_logs(text_to_add: str):
        logger = logging.getLogger('ExecutionLogger')
        logger.info(text_to_add)


if __name__ == '__main__':
    ExecutionLogs.setup_logging()

    ExecutionLogs.add_to_logs("Huh?")
    ExecutionLogs.add_to_logs("Something please")
    ExecutionLogs.add_to_logs("Ł, written without crashing")