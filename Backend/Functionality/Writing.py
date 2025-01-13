import enum
import logging
from pathlib import Path

from typing import Dict, List, Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Personas.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA


class Writing(enum.Enum):
    """Writing represents various task types used within the persona system."""

    @staticmethod
    def determine_files(initial_message: str, tags: Optional[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Determine the list of files to be processed.

        :param initial_message: The user's guidance for writing code.
        :param tags: Additional metadata.
        :return: List of files with their purposes.
        """
        config = Configuration.load_config()
        files = []

        if tags and tags.get("write"):
            file_name = tags.get("write")
            file_name = Writing.check_and_append_extension(file_name)
            files = [{
                "file_name": file_name,
                "purpose": (
                    "This is a new or possibly pre-existing file. "
                    "Your output will be appended here, so write the file without meta commentary."
                )
            }]
        else:
            prompt = (
                "Give just a filename (with extension) that should be worked on given the following prompt. "
                "No commentary. "
                "If appropriate, write multiple files, the ones at the top of the class hierarchy first/on the top."
            ) if config['beta_features']['multi_file_processing_enabled'] else (
                "Give just a filename (with extension) that should be worked on given the following prompt. "
                "No commentary. Select only one singular file alone."
            )

            files_response = AiOrchestrator().execute_function(
                [prompt],
                [initial_message],
                GENERATE_FILE_NAMES_FUNCTION_SCHEMA
            )
            for file in files_response.get('files', []):
                # Check and append extension if needed
                file_name = Writing.check_and_append_extension(file['file_name'])
                purpose = file.get('purpose', '')  # Purpose is optional
                files.append({
                    "file_name": file_name,
                    "purpose": purpose
                })

        logging.info(f"Referencing/Creating the following files: {files}")
        return files

    @staticmethod
    def check_and_append_extension(file_name: str) -> str:
        """
        Check if the provided file name has a valid extension; if not, append '.txt'.

        :param file_name: The file name to check.
        :return: The file name with a valid extension.
        """
        DEFAULT_EXTENSION = 'txt'
        path = Path(file_name)

        if not path.suffix:
            logging.warning(f"File name '{file_name}' has no extension. Appending '.{DEFAULT_EXTENSION}'.")
            return f"{file_name}.{DEFAULT_EXTENSION}"
        return file_name


if __name__ == '__main__':
    pass
