import ast
import enum
import logging
import re
from pathlib import Path

from typing import Dict, List, Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Constants.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA
from Constants.Constants import DEFAULT_EXTENSION
from Constants.Instructions import determine_pages_prompt, DETERMINE_PAGES_SCHEMA


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
                    "This is a new or possibly pre-existing file.\n"
                    "Your output will be appended here, so write the file without meta commentary."
                )
            }]
        else:
            test = AiOrchestrator().execute(
                [determine_pages_prompt(config['beta_features']['multi_file_processing_enabled']),
                 DETERMINE_PAGES_SCHEMA],
                [initial_message],
            )

            pattern = r"<([^>\s]+)(?:\s+purpose='([^']+)')?>"

            # Find all matches using re.findall
            matches = re.findall(pattern, test)

            if not matches:
                logging.warning("No matches found for user topic tags.")

            files = []
            for match in matches:
                file_dict = {
                    "file_name": match[0],
                }
                # Add 'purpose' only if it exists
                if match[1]:
                    file_dict["purpose"] = match[1]
                files.append(file_dict)

        logging.info(f"Referencing/Creating the following files: {files}")
        return files

    @staticmethod
    def check_and_append_extension(file_name: str) -> str:
        """
        Check if the provided file name has a valid extension; if not, append '.txt'.

        :param file_name: The file name to check.
        :return: The file name with a valid extension.
        """
        path = Path(file_name)

        if not path.suffix:
            logging.warning(f"File name '{file_name}' has no extension. Appending '.{DEFAULT_EXTENSION}'.")
            return f"{file_name}.{DEFAULT_EXTENSION}"
        return file_name


if __name__ == '__main__':
    pass
