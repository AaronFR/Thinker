import enum
import logging

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

        if tags and tags.get("write"):
            files = [{
                "file_name": tags.get("write"),
                "purpose": "create from scratch"
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

            files = AiOrchestrator().execute_function(
                [prompt],
                [initial_message],
                GENERATE_FILE_NAMES_FUNCTION_SCHEMA
            )['files']

        logging.info(f"Referencing/Creating the following files: {files}")
        return files






if __name__ == '__main__':
    pass
