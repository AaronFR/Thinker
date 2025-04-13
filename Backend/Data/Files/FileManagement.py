import csv
import os
import logging
import shutil
import yaml

from typing import List, Dict, Any
from deprecated.classic import deprecated

from Constants.Exceptions import file_not_found, file_not_loaded, FAILURE_TO_LIST_STAGED_FILES, \
    FAILURE_TO_READ_FILE, cannot_read_image_file, category_directory_not_found
from Data.Files.StorageBase import StorageBase
from Constants.Constants import DEFAULT_ENCODING
from Utilities.Decorators.Decorators import handle_errors
from Utilities.LogsHandler import LogsHandler


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

    The file management system is intentionally inflexible to prevent
    possible prompt injection and data extraction from outside the designated data areas.
    ONLY information within the boundaries of the 'Files' directory can be edited by the user.

    ToDo: (Bug) tries to create a category folder even when set to s3?
    """

    file_data_directory = os.path.join(os.path.dirname(__file__), '../../../UserData/Files')
    config_data_directory = os.path.join(os.path.dirname(__file__), '../../../UserData/UserConfigs')

    def _get_data_path(self, file_path: str) -> str:
        """Constructs the complete path for the given file_name."""
        return os.path.join(self.file_data_directory, file_path)

    @staticmethod
    def _log_file_action(action: str, file_path: str):
        """Log the action performed on the file."""
        logging.info(f"File {action}: {file_path}")

    @staticmethod
    @handle_errors(raise_errors=True)
    def save_file(content: str, file_path: str, overwrite: bool = False) -> None:
        """
        Saves the response content to a file_name.

        :param content: The content to be formatted and saved.
        :param file_path: The file name with extension prefixed by the category folder id.
        :param overwrite: whether the file_name should be overwritten.

        :raises Exception: If the file size exceeds the limit.
        """

        data_path = FileManagement()._get_data_path(file_path)
        mode = "w" if overwrite or not os.path.exists(data_path) else "a"

        with open(data_path, mode, encoding=DEFAULT_ENCODING) as file:
            file.write(content)
            FileManagement()._log_file_action('saved' if not overwrite else 'overwritten', data_path)

    def read_file(self, full_address: str) -> str:
        """
        Read the content of a specified file.
        ToDo: A retry needs to be added if a file is not detected after upload

        :param full_address: The file name to read, including category folder prefix.
        :return: The content of the file or an error message.
        """
        full_path = self._get_data_path(full_address)
        logging.info(f"Loading file content from: {full_path}")

        if self.is_image_file(full_address):
            logging.warning(f"Attempted to read an image file: {full_address}")
            return cannot_read_image_file(full_address)

        try:
            with open(full_path, 'r', encoding=DEFAULT_ENCODING) as file:
                return file.read()
        except FileNotFoundError:
            logging.exception(file_not_found(full_address))
            return file_not_found(full_address)
        except Exception:
            logging.exception(FAILURE_TO_READ_FILE)
            return file_not_loaded(full_address)

    @handle_errors()
    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Move a file to a new path within the file management system.

        :param current_path: The path of the current file.
        :param new_path: The destination path for the file.
        """
        shutil.move(self._get_data_path(current_path), self._get_data_path(new_path))
        self._log_file_action('moved', f"{current_path} to {new_path}")

    @staticmethod
    def save_yaml(yaml_path: str, data: Dict[Any, Any]) -> None:
        """
        Saves a dictionary to a YAML file at the specified path.

        :param yaml_path: The path to the YAML file.
        :param data: The dictionary to save.
        """
        yaml_content = yaml.safe_dump(data)
        full_path = os.path.join(FileManagement.config_data_directory, yaml_path)
        FileManagement.save_file(yaml_content, full_path, overwrite=True)

    @staticmethod
    def load_yaml(yaml_path: str) -> Dict[str, object]:
        """
        Loads existing data from a YAML file if available.

        :param yaml_path: The path to the YAML file.
        :return: A dictionary containing the loaded data or an empty dictionary.
        """
        existing_data = {}
        full_path = os.path.join(FileManagement.config_data_directory, yaml_path)

        try:
            if os.path.isfile(full_path) and os.path.getsize(full_path) > 0:
                with open(full_path, 'r', encoding=DEFAULT_ENCODING) as yaml_file:
                    existing_data = yaml.safe_load(yaml_file) or {}
            else:
                logging.info(f"No existing data file found at {full_path}.")
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Error reading YAML file: {e}")

        return existing_data

    @staticmethod
    def list_files(category_id: str) -> List[str]:
        """
        List all files in a specific category folder

        NOTE: Currently unused.

        :return: A list of staged file paths.
        """
        directory = os.path.join(FileManagement.file_data_directory, category_id)

        try:
            entries = os.listdir(directory)
            file_paths = [os.path.join(category_id, entry) for entry in entries
                          if os.path.isfile(os.path.join(category_id, entry))]

            logging.info(f"Found the following files in category directory {category_id}: {file_paths}")
            return file_paths
        except FileNotFoundError:
            logging.exception(category_directory_not_found(directory))
            return []
        except Exception:
            logging.exception(FAILURE_TO_LIST_STAGED_FILES)
            return []

    @staticmethod
    def get_numbered_string(lines: List[str]) -> str:
        """Returns a str where each line is prepended with its line-number."""
        return ''.join([f"{i + 1}: {line}" for i, line in enumerate(lines)])

    @staticmethod
    def write_to_csv(file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        """
        Writes or appends a list of dictionaries to a CSV file.

        :param file_name: The name of the CSV file.
        :param dictionaries: A list of dictionaries to write to the file.
        :param fieldnames: The field names for the CSV header.
        """
        logging.info(f"Data being written to CSV: {dictionaries}")
        file_path = os.path.join(os.path.dirname(__file__), '../../UserData/DataStores', file_name)

        mode = 'a' if os.path.isfile(file_path) and os.path.getsize(file_path) > 0 else 'w'
        with open(file_path, mode=mode, newline='', encoding=DEFAULT_ENCODING) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if mode == 'w':
                writer.writeheader()

            if isinstance(dictionaries, list) and all(isinstance(item, dict) for item in dictionaries):
                writer.writerows(dictionaries)
            else:
                logging.error("Error: Data is not a list of dictionaries!")

    @deprecated("Should just use save_yaml")
    @staticmethod
    @handle_errors(raise_errors=True)
    def write_to_yaml(data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        """
        Writes the combined page data to a YAML file.

        :param data: The data to write to the YAML file.
        :param yaml_path: The path where the YAML file will be saved.
        :param overwrite: Determines if the YAML should be replaced or merely appended to.
        """
        mode = "w" if overwrite or not os.path.exists(yaml_path) else "a"
        with open(yaml_path, mode, encoding=DEFAULT_ENCODING) as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, Dumper=MyDumper, allow_unicode=True)

    @staticmethod
    def regex_refactor(target_string: str, replacement: str, file_path: str) -> None:
        """
        Replaces every instance of the target with the replacement str.

        :param target_string: The text to be replaced.
        :param replacement: The text to replace the target string.
        :param file_path: The file path including category prefix.
        :raises ValueError: if the rewrite operation fails.
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
    def add_new_category_folder(category_id: str) -> None:
        """
        Creates a category folder locally for a new category.
        ToDo: This will need to be changed when s3 is adapted to resemble local storage
         that is UserData/Files/UserId?/Categories

        :param category_id: The new folder id to create.
        """
        new_directory = os.path.join(FileManagement.file_data_directory, category_id)
        os.makedirs(new_directory, exist_ok=True)  # Create new folder for the given id


if __name__ == '__main__':
    numbered_lines = FileManagement().read_file("test/Writing.py")
    print(numbered_lines)
