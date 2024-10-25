import enum
import os
import py_compile
import subprocess
from typing import Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Utilities.ExecutionLogs import ExecutionLogs
from Data.FileManagement import FileManagement
from Personas.PersonaSpecification import PersonaConstants


class Coding(enum.Enum):
    """Coding is an enumeration representing various task types used within the persona system.

    Methods:
        - WRITING: write new code file
    """

    @staticmethod
    def write_to_file_task(task_parameters: Dict[str, object]):
        """
        Repeatedly writes content to the specified number of pages. Where one page roughly corresponds to 500 words
        (2000 tokens output)

        :param task_parameters: Dict with SAVE_TO and INSTRUCTION
        """
        executor = AiOrchestrator(task_parameters.get(PersonaConstants.REFERENCE, []))
        output = executor.execute(
            ["Just write the code from the following input, strip out any code block designators, e.g. ```python...```"],
            [task_parameters[PersonaConstants.INSTRUCTION]]
        )

        FileManagement.save_file(output, task_parameters[PersonaConstants.SAVE_TO], overwrite=True)
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
    def check_syntax(file_path: str) -> bool | str:
        """
        ToDo: implement
        ToDo: Assuming that script is written in python

        :param file_path: including category, file name and extension
        :returns: whether or not the coding file successfully complies and if it doesn't a message explaining
         why not
        """
        script_path = os.path.join(FileManagement.file_data_directory, file_path)
        try:
            py_compile.compile(script_path, doraise=True)
            return True
        except py_compile.PyCompileError as e:
            return f"Syntax error: {e.msg}"

    @staticmethod
    def run_generated_script(file_path: str) -> str:
        """
        ToDo: implement + add method to check IF a script should be run
        ToDo: Write method for running tests (depending on chosen framework)
        :param file_path: including category, file name and extension
        :returns: the output of the script or -if an error is encountered the error message
        """
        script_path = os.path.join(FileManagement.file_data_directory, file_path)
        try:
            result = subprocess.run(['python', script_path], capture_output=True, text=True, check=True)
            return f"Script Output:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Error running the script:\n{e.stderr}"


if __name__ == '__main__':
    pass
