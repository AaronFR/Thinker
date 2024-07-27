import os
import logging
from typing import List


class FileManagement:
    """Class for managing files related to thoughts and solutions."""

    @staticmethod
    def initialise_file(thought_id: int, file: str):
        """Initialize a given file as an empty file, in advance of it being opened
        ToDo: Thoughts as a folder and Thoughts as a class do not match up. One thought has numerous Thought class
        instance declarations, doesn't make sense.

        :param thought_id: The ID of the currently executing thought.
        :param file: The name of the file to initialize.
        """
        os.makedirs(f"Thoughts/{thought_id}", exist_ok=True)
        file_path = os.path.join("Thoughts", str(thought_id), file)
        try:
            with open(file_path, "w", encoding="utf-8"):
                logging.info(f"File {file_path} instantiated.")
        except Exception as e:
            logging.error(f"ERROR: could not instantiate file: {file_path}\n {str(e)} \nThought_id: {thought_id}")

    @staticmethod
    def list_files(directory: str) -> list:
        """
        List all file names in the given directory.

        :param directory: The path to the directory.
        :return: A list of file names in the directory.
        """
        try:
            entries = os.listdir(directory)
            file_names = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
            logging.info(f"Found the following files in Thought space: {file_names}")

            return file_names
        except FileNotFoundError:
            logging.error(f"The directory {directory} does not exist.")
            return []
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return []

    @staticmethod
    def read_file(file_path: str) -> str:
        """Read the content of a file.

        :param file_path: The path of the file to read.
        :return: The content of the file or an error message to let the next llm known what happened.
        """
        full_path = os.path.join("Thoughts", "1", file_path)
        logging.info(f"Loading file content from: {full_path}")
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return f"[FAILED TO LOAD {file_path}]"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return f"[FAILED TO LOAD {file_path}]"

    @staticmethod
    def read_files(file_paths: List[str]) -> List[str]:
        """Read content from multiple files.

        :param file_paths: List of file paths to read.
        :return: List of content read from the files.
        """
        contents = []
        for path in file_paths:
            logging.info(f"Attempting to access {path}")
            contents.append(FileManagement.read_file(path))
        return contents

    @staticmethod
    def save_file(content: str, file_name, thought_id: str, overwrite=False):
        """
        Saves the response content in HTML format to a file.

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the output HTML file.
        :param thought_id: sub-folder the ThoughtProcess is running on
        :param overwrite: whether the file should be overwritten
        """
        file_path = os.path.join("Thoughts", thought_id, file_name)
        try:
            if overwrite:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                    logging.debug("File overwritten: {file_path}")
            else:
                with open(file_path, "a", encoding="utf-8") as file:
                    file.write(content)
                    logging.debug("File Saved: {file_path}")
        except Exception as e:
            logging.error(f"could not save file, {str(e)}")
