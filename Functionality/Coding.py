import enum
import os
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


if __name__ == '__main__':
    pass
