import os
import logging
import re
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
        Saves the response content to a file.

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the file
        :param thought_id: sub-folder the ThoughtProcess is running on
        :param overwrite: whether the file should be overwritten
        """
        file_path = os.path.join("Thoughts", thought_id, file_name)
        try:
            if overwrite:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                    logging.info(f"File overwritten: {file_path}")
            else:
                with open(file_path, "a", encoding="utf-8") as file:
                    file.write(content)
                    logging.info(f"File Saved: {file_path}")
        except Exception as e:
            logging.error(f"could not save file, {str(e)}")

    @staticmethod
    def re_write_section(target_string: str, replacement: str, file_name, thought_id: str):
        """
        Replaces every instance of the target with the replacement str

        :param target_string: The text to be replaced
        :param replacement: to replace target_string
        :param file_name: The base name for the file
        :param thought_id: sub-folder the ThoughtProcess is running on
        """
        file_content = FileManagement.read_file(file_name)

        # pattern = re.compile(re.escape(target_string), re.DOTALL)

        # Escape special characters in the stripped string
        escaped_string = re.escape(target_string)
        # Replace escaped spaces and newline characters with \s+ for flexible matching
        flexible_pattern = re.sub(r'\\ ', r'\\s+', escaped_string)
        # Replace escaped newlines with \s+ for flexible matching
        flexible_pattern = re.sub(r'\\n', r'\\s+', flexible_pattern)
        pattern = re.compile(flexible_pattern, re.DOTALL)

        modified_text = pattern.sub(replacement, file_content)


        if file_content == modified_text:
            # ToDo add backup method to try and recover
            logging.error(f"No matches found for the target string: {target_string}")
            raise ValueError(f"No matches found for the target string: {target_string}")

        try:
            file_path = os.path.join("Thoughts", thought_id, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_text)
                logging.info(f"File overwritten: {file_path}")
        except Exception as e:
            logging.error(f"could not save file, {str(e)}")


if __name__ == '__main__':
    FileManagement.re_write_section("""Generate a response based on system and user prompts.
        
        ToDo: At some point actions other than writing will be needed, e.g. 'web search'.""", "womp", "thought.py", "1")
