import csv
import os
import logging
from typing import List
from datetime import datetime
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from Utilities import Globals, Constants
from Utilities.Constants import DEFAULT_ENCODING
from Utilities.ErrorHandler import ErrorHandler


class FileManagement:
    """Class for managing files related to tasks and solutions."""

    thoughts_directory = os.path.join(os.path.dirname(__file__), '..', 'thoughts')

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    def initialise_file(file_name: str):
        """Initialise a given file as an empty file, in advance of it being opened

        :param file_name: The name of the file to initialise
        """
        directory_path = os.path.join(FileManagement.thoughts_directory, str(Globals.current_thought_id))
        file_path = os.path.join(directory_path, file_name)
        try:
            os.makedirs(directory_path, exist_ok=True)
            with open(file_path, "w", encoding=Constants.DEFAULT_ENCODING):
                logging.info(f"Successfully created and opened file: {file_path}.")
        except Exception:
            logging.exception(f"ERROR: Failed to create directory or open file: {file_path}.")

    @staticmethod
    def list_file_names() -> List[str]:
        """List all file_name names in the given directory.
        ToDo: should leave files tagged meta alone, as soon as we start tagging meta files...

        :return: A list of file_name names in the directory
        """
        thought_directory = FileManagement._get_thought_folder()
        try:
            entries = os.listdir(thought_directory)
            file_names = [entry for entry in entries if os.path.isfile(os.path.join(thought_directory, entry))]
            logging.info(f"Found the following files in Thought space: {file_names}")

            return file_names
        except FileNotFoundError:
            logging.exception(f"The directory {thought_directory} does not exist.")
            return []
        except Exception:
            logging.exception(f"An error occurred")
            return []

    @staticmethod
    def get_numbered_lines(lines):
        return ''.join([f"{i + 1}: {line}" for i, line in enumerate(lines)])

    @staticmethod
    def read_file(file_path: str, return_numbered_lines: bool = False) -> str:
        """Read the content of a specified file.

        :param file_path: The path of the file_name to read
        :param return_numbered_lines: Flag to determine if the content should be returned as numbered lines
        :return: The content of the file or an error message to inform the next LLM what happened
        """
        full_path = os.path.join(FileManagement.thoughts_directory, str(Globals.current_thought_id), file_path)
        logging.info(f"Loading file_name content from: {full_path}")

        try:
            with open(full_path, 'r', encoding=Constants.DEFAULT_ENCODING) as file:
                if return_numbered_lines:
                    return FileManagement.get_numbered_lines(file.readlines())
                else:
                    return file.read()
        except FileNotFoundError:
            logging.exception(f"File not found: {file_path}")
            return f"[FAILED TO LOAD {file_path}]"
        except Exception:
            logging.exception(f"An unexpected error occurred")
            return f"[FAILED TO LOAD {file_path}]"

    @staticmethod
    def read_file_with_lines(file_path: str) -> List[str]:
        """Read the content of a file, with line numbers prepended to each line.

        :param file_path: The path of the file to read
        :return: The content of the file with line numbers, or an error message to let the next LLM know what happened
        """
        full_path = os.path.join(FileManagement.thoughts_directory, str(Globals.current_thought_id), file_path)
        logging.info(f"Loading file content from: {full_path}")
        try:
            with open(full_path, 'r', encoding=Constants.DEFAULT_ENCODING) as file:
                return file.readlines()
        except FileNotFoundError:
            logging.exception(f"File not found: {file_path}")
            return [f"[FAILED TO LOAD {file_path}]"]
        except Exception:
            logging.exception(f"An unexpected error occurred")
            return [f"[FAILED TO LOAD {file_path}]"]

    @staticmethod
    def read_files(file_paths: List[str]) -> List[str]:
        """Read content from multiple files.

        :param file_paths: List of file_name paths to read
        :return:  List of content read from the specified files
        """
        return [FileManagement.read_file(path) for path in file_paths]

    @staticmethod
    def save_file(content: str, file_name, overwrite=False):
        """Saves the response content to a file_name.

        :param content: The content to be formatted and saved
        :param file_name: The base name for the file_name, (only the file_name name, no absolute or relative references)
        :param overwrite: whether the file_name should be overwritten
        """
        file_path = FileManagement._get_file_path(file_name)
        mode = "w" if overwrite or not os.path.exists(file_path) else "a"
        try:
            with open(file_path, mode, encoding=DEFAULT_ENCODING) as file:
                file.write(content)
                logging.info(f"File {'overwritten' if overwrite else 'saved'}: {file_path}")
        except Exception:
            logging.exception(f"ERROR: could not save file_name: {file_path}")

    @staticmethod
    def regex_refactor(target_string: str, replacement: str, file_name):
        """Replaces every instance of the target with the replacement str

        :param target_string: The text to be replaced
        :param replacement: The text to replace the target string
        :param file_name: The base name for the file_name
        :raises ValueError: if the rewrite operation fails
        """
        file_content = FileManagement.read_file(file_name)
        modified_text = FileManagement._replace_text(file_content, target_string, replacement)

        if file_content == modified_text:
            # You could try and recover but really the lesson is: don't use regex just *extract* lines from the document
            # and have the AI operate on those lines directly.
            logging.error(f"No matches found for the target string: {target_string}")
            raise ValueError(f"No matches found for the target string: {target_string}")

        FileManagement._write_to_file(modified_text, file_name)

    @staticmethod
    def _replace_text(content: str, target: str, replacement: str) -> str:
        """Replaces every instance of the target with the replacement using simple string methods.

        :param content: The original content in which to replace text
        :param target: The text to be replaced
        :param replacement: The text to replace the target string
        :return: The modified content
        """
        return content.replace(target, replacement)

    @staticmethod
    def _write_to_file(content: str, file_name: str):
        """Write the content to a file_name.

        :param content: The content to be written
        :param file_name: The name of the file_name
        """
        file_path = FileManagement._get_file_path(file_name)
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
                logging.info(f"File overwritten: {file_path}")
        except Exception:
            logging.exception(f"ERROR: could not save file_name: {file_path}")

    @staticmethod
    def save_content_as_html(content: str, file_name: str, prompt_id: str):
        """Saves the response content in HTML format to a given file.

        :param content: The content to be formatted and saved
        :param file_name: The base name for the output HTML file_name
        :param prompt_id: An identifier to make the file_name name unique
        """
        dir_path = os.path.join(FileManagement.thoughts_directory, str(prompt_id))
        os.makedirs(dir_path, exist_ok=True)

        html_text = FileManagement._format_to_html(content)
        file_path = dir_path + f"/{file_name}_{prompt_id}.html"

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_text)
                logging.info(f"HTML file_name saved: {file_path}")
        except Exception:
            logging.exception(f"Could not save HTML file_name: {file_path}")

    @staticmethod
    def _format_to_html(text: str) -> str:
        """Formats the provided text as HTML.

        :param text: Initial text with format characters e.g. \n
        :return: HTML formatted string of the input text
        """
        html_formatter = HtmlFormatter(full=True)
        highlighted_code = highlight(text, PythonLexer(), html_formatter)
        return highlighted_code

    @staticmethod
    def aggregate_files(file_base_name, start, end):
        """Aggregate file content from multiple files into a single file.

        :param file_base_name: The base name for the files to aggregate
        :param start: The starting index for the range of files to aggregate
        :param end: The ending index for the range of files to aggregate
        """
        files_content = FileManagement._read_files_in_range(file_base_name, start, end)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        FileManagement.save_content_as_html(files_content, "solution", timestamp)
        FileManagement.save_file(files_content, "solution", overwrite=True)

    @staticmethod
    def _read_files_in_range(file_base_name: str, start: int, end: int) -> str:
        """Read content from files in the specified range.

        :param file_base_name: The base name for the files
        :param start: The starting index for the files
        :param end: The ending index for the files
        :return: The aggregated content from the files
        """
        files_content = ""
        for i in range(start, end + 1):
            file_path = f"{file_base_name}_{i}.txt"
            try:
                with open(file_path, 'r', encoding=Constants.DEFAULT_ENCODING) as file:
                    files_content += file.read()
                logging.info(f"CONTENT [{i}]: {files_content}")
            except FileNotFoundError:
                logging.exception(f"File not found: {file_path}")
            except UnicodeDecodeError:
                logging.exception(f"Error decoding file_name {file_path}")
            except Exception:
                logging.exception(f"Could not read file_name {file_path}")
        return files_content

    @staticmethod
    def get_current_thought_id() -> int:
        """Get the next available thought ID based on existing directories.

        :return: Next available thought ID as an integer
        """
        os.makedirs(FileManagement.thoughts_directory, exist_ok=True)
        return len([name for name in os.listdir(FileManagement.thoughts_directory) if
                    os.path.isdir(os.path.join(FileManagement.thoughts_directory, name))]) + 1

    @staticmethod
    def _get_file_path(file_name: str) -> str:
        """Get the full path for a file_name in the given thought and file_name name.

        :param file_name: The name of the file_name
        :return: The full path of the file_name
        """
        return os.path.join(FileManagement.thoughts_directory, str(Globals.current_thought_id), file_name)

    @staticmethod
    def _get_thought_folder() -> str:
        """Get the folder path for a given thought ID.

        :return: The folder path for the given thought ID
        """
        return os.path.join(FileManagement.thoughts_directory, str(Globals.current_thought_id))

    @staticmethod
    def write_to_csv(file_name, dictionaries, fieldnames):
        """
        Writes a list of dictionaries to a brand new CSV file.
        """

        logging.info(f"Data being written to CSV: {dictionaries}")
        file_path = os.path.join(os.path.dirname(__file__), 'DataStores', file_name)

        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
        mode = 'a' if file_exists else 'w'
        with open(file_path, mode=mode, newline='', encoding=DEFAULT_ENCODING) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            if isinstance(dictionaries, list) and all(isinstance(item, dict) for item in dictionaries):
                writer.writerows(dictionaries)
            else:
                logging.error("Error: Data is not a list of dictionaries!")


if __name__ == '__main__':
    numbered_lines = FileManagement.read_file("Writing.py", return_numbered_lines=True)
    print(numbered_lines)



