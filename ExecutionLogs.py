import Constants
import Globals
from ThoughtProcessor.FileManagement import FileManagement


class ExecutionLogs:

    @staticmethod
    def add_to_logs(text_to_add: str):
        Globals.execution_logs += text_to_add + "\n"

    @staticmethod
    def save_execution_logs():
        FileManagement.save_file(Globals.execution_logs, Constants.execution_logs_filename, overwrite=True)
