import enum
import logging
import os
import py_compile
import subprocess
from typing import Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Decorators import return_for_error
from Utilities.ErrorHandler import ErrorHandler
from Utilities.ExecutionLogs import ExecutionLogs
from Personas.PersonaSpecification import PersonaConstants


class Coding(enum.Enum):
    """Coding is an enumeration representing various task types used within the persona system.

    Methods:
        - WRITING: write new code file
    """

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    def write_to_file_task(task_parameters: Dict[str, object], overwrite=True):
        """
        Repeatedly writes content to the specified number of pages. Where one page roughly corresponds to 500 words
        (2000 tokens output)

        :param task_parameters: Dict with SAVE_TO and INSTRUCTION
        :param overwrite: Whether the original file should be overwritten
        """
        logging.info(f"Writing to file task initiated with the following parameters: {task_parameters}")
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        output = executor.execute(
            ["Just write the code from the following input, strip out any code block designators, e.g. ```python...```"],
            [task_parameters[PersonaConstants.INSTRUCTION]]
        )

        StorageMethodology.select().save_file(output, task_parameters[PersonaConstants.SAVE_TO], overwrite=overwrite)
        ExecutionLogs.add_to_logs(f"Saved to {task_parameters[PersonaConstants.SAVE_TO]}")

    @staticmethod
    def is_coding_file(file_name):
        # List of common coding file extensions
        coding_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.rb', '.php', '.html', '.css', '.go', '.ts', '.cs'}

        # Get the file extension
        _, extension = os.path.splitext(file_name)

        # Check if the file extension is in the list
        return extension in coding_extensions

    @staticmethod
    @return_for_error(lambda e: f"Syntax error: {getattr(e, 'msg', 'Unknown error')}")
    def check_syntax(file_path: str) -> bool | str:
        """
        ToDo: implement
        ToDo: Assuming that script is written in python

        :param file_path: including category, file name and extension
        :returns: whether the coding file successfully complies and if it doesn't a message explaining
         why not
        """
        script_path = os.path.join(FileManagement.file_data_directory, file_path)

        py_compile.compile(script_path, doraise=True)
        return True

    @staticmethod
    @return_for_error(
        lambda e: f"Error running the script: {getattr(e, 'stderr', 'No error output')}")
    def run_generated_script(file_path: str) -> str:
        """
        ToDo: implement + add method to check IF a script should be run
        ToDo: Write method for running tests (depending on chosen framework)
        :param file_path: including category, file name and extension
        :returns: the output of the script or -if an error is encountered the error message
        """
        script_path = os.path.join(FileManagement.file_data_directory, file_path)
        result = subprocess.run(['python', script_path], capture_output=True, text=True, check=True)
        return f"Script Output:\n{result.stdout}"


if __name__ == '__main__':
    pass
