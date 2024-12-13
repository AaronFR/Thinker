import csv
import os
import logging
import shutil

import yaml

from typing import List, Dict

from Data.Files.StorageBase import StorageBase
from Utilities import Constants
from Utilities.Constants import DEFAULT_ENCODING
from Utilities.Decorators import handle_errors
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Contexts import get_user_context


class MyDumper(yaml.Dumper):
    """
    Custom YAML dumper that formats multi-line strings using block style.
    """
    def represent_scalar(self, tag, value: str, style=None) -> yaml.nodes.ScalarNode:
        if '\n' in value or isinstance(value, str):
            return super().represent_scalar(tag, value, style='|')
        return super().represent_scalar(tag, value, style)


class FileManagement(StorageBase):
    """
    Class for managing files related to tasks and solutions.

    Its worth noting the file management system as a whole has a deliberately in-flexible system to prevent
    possible prompt injection and extraction of data from outside the designated data areas.
    ONLY information within the boundaries of the 'FileData' directory can be edited by the user.
    """

    file_data_directory = os.path.join(os.path.dirname(__file__), '../FileData')

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    @handle_errors(raise_errors=True)
    def save_file(content: str, file_path, overwrite: bool = False):
        """
        Saves the response content to a file_name.

        :param content: The content to be formatted and saved
        :param file_path: The file name with extension prefixed by the category folder id
        :param overwrite: whether the file_name should be overwritten
        """
        data_path = os.path.join(FileManagement.file_data_directory, file_path)
        mode = "w" if overwrite or not os.path.exists(data_path) else "a"
        with open(data_path, mode, encoding=DEFAULT_ENCODING) as file:
            file.write(content)
            logging.info(f"File {'overwritten' if overwrite else 'saved'}: {data_path}")

    def read_file(self, full_address: str) -> str:
        """Read the content of a specified file.
        ToDo: A retry needs to be added if a file is not detected after upload

        :param full_address: The file name to read, including category folder prefix
        :return: The content of the file or an error message to inform the next LLM what happened
        """
        full_path = os.path.join(FileManagement.file_data_directory, full_address)
        logging.info(f"Loading file_name content from: {full_path}")

        if self.is_image_file(full_address):
            logging.warning(f"Attempted to read an image file: {full_address}")
            return f"[CANNOT READ IMAGE FILE: {full_address}]"

        try:
            with open(full_path, 'r', encoding=Constants.DEFAULT_ENCODING) as file:
                return file.read()
        except FileNotFoundError:
            logging.exception(f"File not found: {full_address}")
            return f"[FILE NOT FOUND {full_address}]"
        except Exception:
            logging.exception(f"An unexpected error occurred")
            return f"[FAILED TO LOAD {full_address}]"

    def move_file(self, current_path: str, new_path: str):
        try:
            staged_file_path = os.path.join(FileManagement.file_data_directory, current_path)
            new_file_path = os.path.join(FileManagement.file_data_directory, new_path)
            shutil.move(staged_file_path, new_file_path)
            logging.info(f"{current_path} moved to {new_path}")
        except Exception:
            logging.exception("failed to move local files")


    @staticmethod
    def list_staged_files() -> List[str]:
        """List all files in
        ToDo: should include the directory in the file path
        ToDo: should leave files tagged meta alone, as soon as we start tagging meta files...

        :return: A list of staged file paths that belong to the user staging directory
        """
        user_id = get_user_context()
        staging_directory = os.path.join(FileManagement.file_data_directory, user_id)
        try:
            entries = os.listdir(staging_directory)
            file_paths = [os.path.join(user_id, entry) for entry in entries
                          if os.path.isfile(os.path.join(staging_directory, entry))]
            logging.info(f"Found the following files in Thought space: {file_paths}")

            return file_paths
        except FileNotFoundError:
            logging.exception(f"The directory {staging_directory} does not exist.")
            return []
        except Exception:
            logging.exception(f"An error occurred")
            return []

    @staticmethod
    def get_numbered_string(lines) -> str:
        """Returns a str where each line is prepended with its line-number"""
        return ''.join([f"{i + 1}: {line}" for i, line in enumerate(lines)])

    @staticmethod
    def write_to_csv(file_name, dictionaries, fieldnames):
        """
        Writes or appends a list of dictionaries to a brand new CSV file.
        """

        logging.info(f"Data being written to CSV: {dictionaries}")
        file_path = os.path.join(os.path.dirname(__file__), 'DataStores', file_name)

        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
        mode = 'a' if file_exists else 'w'
        with open(file_path, mode=mode, newline='', encoding=DEFAULT_ENCODING) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            if isinstance(dictionaries, list) and all(isinstance(item, dict) for item in dictionaries):
                writer.writerows(dictionaries)
            else:
                logging.error("Error: Data is not a list of dictionaries!")

    @staticmethod
    @handle_errors(raise_errors=True)
    def write_to_yaml(data: Dict[str, object], yaml_path: str, overwrite=False) -> None:
        """
        Writes the combined page data to a YAML file.

        :param data: The data to write to the YAML file.
        :param yaml_path: The path where the YAML file will be saved.
        :param overwrite: Determines if the yaml should be replaced or merely appended to
        """
        mode = "w" if overwrite or not os.path.exists(yaml_path) else "a"
        with open(yaml_path, mode, encoding=DEFAULT_ENCODING) as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, Dumper=MyDumper, allow_unicode=True)

    @staticmethod
    def load_yaml(yaml_path: str) -> Dict[str, object]:
        """
        Loads existing data from a YAML file if available.

        :param yaml_path: The path to the YAML file.
        :return: A dictionary containing the loaded data or an empty dictionary.
        """
        existing_data = {}

        if os.path.isfile(yaml_path) and os.path.getsize(yaml_path) > 0:
            try:
                with open(yaml_path, 'r', encoding=DEFAULT_ENCODING) as yaml_file:
                    existing_data = yaml.safe_load(yaml_file) or {}
            except (FileNotFoundError, yaml.YAMLError) as e:
                logging.error(f"Error reading YAML file: {e}")
        else:
            logging.info(f"No existing data file found at {yaml_path}.")

        return existing_data

    @staticmethod
    def regex_refactor(target_string: str, replacement: str, file_path):
        """Replaces every instance of the target with the replacement str

        :param target_string: The text to be replaced
        :param replacement: The text to replace the target string
        :param file_path: The file path including category prefix
        :raises ValueError: if the rewrite operation fails
        """
        file_content = FileManagement().read_file(file_path)
        modified_text = file_content.replace(target_string, replacement)

        if file_content == modified_text:
            # You could try and recover but really the lesson is: don't use regex just *extract* lines from the document
            # and have the AI operate on those lines directly.
            logging.error(f"No matches found for the target string: {target_string}")
            raise ValueError(f"No matches found for the target string: {target_string}")

        FileManagement.save_file(modified_text, file_path)

    @staticmethod
    def add_new_user_file_folder(user_id: int) -> None:
        """
        Creates a new file staging folder for the new user

        :param user_id: The new folder id to create
        """
        new_directory = os.path.join(FileManagement.file_data_directory, str(user_id))
        os.makedirs(new_directory, exist_ok=True)


if __name__ == '__main__':
    numbered_lines = FileManagement().read_file("test/Writing.py")
    print(numbered_lines)
