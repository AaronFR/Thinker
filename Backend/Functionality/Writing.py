import ast
import enum
import logging
import re
from pathlib import Path

from typing import Dict, List, Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Constants.Constants import DEFAULT_EXTENSION, TAG_WITH_PURPOSE_REGEX
from Constants.Instructions import determine_pages_prompt, DETERMINE_PAGES_SCHEMA


class Writing(enum.Enum):
    """Writing represents various task types used within the worker system."""

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
            files_suggested = AiOrchestrator().execute(
                [
                    DETERMINE_PAGES_SCHEMA,
                    determine_pages_prompt(config['files']['multi_file_processing_enabled'])
                 ],
                [initial_message],
            )


            # Find all matches using re.findall
            matches = re.findall(TAG_WITH_PURPOSE_REGEX, files_suggested)

            files = []
            if matches:
                for match in matches:
                    file_dict = {
                        "file_name": match[0],
                    }
                    # Add 'purpose' only if it exists
                    if match[1]:
                        file_dict["purpose"] = match[1]
                    files.append(file_dict)
            else:
                logging.warning("No matches found for user topic tags.")
                file_dict = {
                    "file_name": "default.txt",
                    "purpose": files_suggested
                }
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
