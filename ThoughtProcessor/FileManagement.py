import os
import logging
import re
from typing import List
from datetime import datetime
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

import Globals
from ThoughtProcessor.ErrorHandler import ErrorHandler


class FileManagement:
    """Class for managing files related to tasks and solutions."""

    thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    def initialise_file(file: str):
        """Initialise a given file as an empty file, in advance of it being opened
        instance declarations, doesn't make sense.

        :param file: The name of the file to initialise.
        """
        os.makedirs(f"thoughts/{Globals.thought_id}", exist_ok=True)
        file_path = os.path.join("thoughts", str(Globals.thought_id), file)
        try:
            with open(file_path, "w", encoding="utf-8"):
                logging.info(f"File {file_path} instantiated.")
        except Exception as e:
            logging.error(f"""ERROR: could not instantiate file: {file_path}\n{str(e)}""")

    @staticmethod
    def list_files(thought_id: str = "1") -> list:
        """
        List all file names in the given directory.

        :return: A list of file names in the directory.
        """
        thought_folder = FileManagement._get_thought_folder(thought_id)
        try:
            entries = os.listdir(thought_folder)
            file_names = [entry for entry in entries if os.path.isfile(os.path.join(thought_folder, entry))]
            logging.info(f"Found the following files in Thought space: {file_names}")

            return file_names
        except FileNotFoundError:
            logging.error(f"The directory {thought_folder} does not exist.")
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
        full_path = os.path.join(FileManagement.thoughts_folder, str(Globals.thought_id), file_path)
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
        return [FileManagement.read_file(path) for path in file_paths]

    @staticmethod
    def save_file(content: str, file_name, overwrite=False):
        """
        Saves the response content to a file.

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the file, (only the file name, no absolute or relative references)
        :param overwrite: whether the file should be overwritten
        """
        file_path = FileManagement._get_file_path(file_name)
        mode = "w" if overwrite or not os.path.exists(file_path) else "a"
        try:
            with open(file_path, mode, encoding="utf-8") as file:
                file.write(content)
                logging.info(f"File {'overwritten' if overwrite else 'saved'}: {file_path}")
        except Exception as e:
            logging.error(f"ERROR: could not save file: {file_path}\n {str(e)}")

    @staticmethod
    def re_write_section(target_string: str, replacement: str, file_name):
        """
        Replaces every instance of the target with the replacement str

        :param target_string: The text to be replaced.
        :param replacement: The text to replace the target string.
        :param file_name: The base name for the file.
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
        # pattern = re.compile(re.escape(target_string), re.DOTALL)

        # Escape special characters in the stripped string
        escaped_string = re.escape(target)
        # Replace escaped spaces and newline characters with \s+ for flexible matching
        flexible_pattern = re.sub(r'\\ ', r'\\s+', escaped_string)
        # Replace escaped newlines with \s+ for flexible matching
        flexible_pattern = re.sub(r'\\n', r'\\s+', flexible_pattern)
        pattern = re.compile(flexible_pattern, re.DOTALL)

        return pattern.sub(replacement, content)

    @staticmethod
    def _write_to_file(content: str, file_name: str):
        """Write the content to a file.

        :param content: The content to be written.
        :param file_name: The name of the file.
        """
        file_path = FileManagement._get_file_path(file_name)
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
                logging.info(f"File overwritten: {file_path}")
        except Exception as e:
            logging.error(f"ERROR: could not save file: {file_path}\n {str(e)}")

    @staticmethod
    def save_as_html(content: str, file_name: str, prompt_id: str):
        """
        Saves the response content in HTML format to a file.

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the output HTML file.
        :param prompt_id: An identifier to make the file name unique.
        """
        dir_path = os.path.join(FileManagement.thoughts_folder, str(prompt_id))
        os.makedirs(dir_path, exist_ok=True)

        html_text = FileManagement._format_to_html(content)
        file_path = dir_path + f"/{file_name}_{prompt_id}.html"

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_text)
                logging.info(f"HTML file saved: {file_path}")
        except Exception as e:
            logging.error(f"Could not save HTML file: {file_path}\n {str(e)}")

    @staticmethod
    def _format_to_html(text: str) -> str:
        """
        Formats the provided text as HTML.
        :param text: Initial text with format characters e.g. \n
        :return: HTML formatted string of the input text.
        """
        html_formatter = HtmlFormatter(full=True)
        highlighted_code = highlight(text, PythonLexer(), html_formatter)
        return highlighted_code

    @staticmethod
    def aggregate_files(file_base_name, start, end):
        """Aggregate content from multiple files into a single file.

        :param file_base_name: The base name for the files to aggregate.
        :param start: The starting index for the files.
        :param end: The ending index for the files.
        """
        content = FileManagement._read_files_in_range(file_base_name, start, end)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        FileManagement.save_as_html(content, "solution", timestamp)
        FileManagement.save_file(content, "solution", overwrite=True)

    @staticmethod
    def _read_files_in_range(file_base_name: str, start: int, end: int) -> str:
        """Read content from files in the specified range.

        :param file_base_name: The base name for the files.
        :param start: The starting index for the files.
        :param end: The ending index for the files.
        :return: The aggregated content from the files.
        """
        content = ""
        for i in range(start, end + 1):
            file_path = f"{file_base_name}_{i}.txt"
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content += file.read()
                logging.info(f"CONTENT [{i}]: {content}")
            except FileNotFoundError:
                logging.error(f"File not found: {file_path}")
            except UnicodeDecodeError as e:
                logging.error(f"Error decoding file {file_path}: {e}")
            except Exception as e:
                logging.error(f"ERROR: could not read file {file_path}\n {str(e)}")
        return content

    @staticmethod
    def get_next_thought_id() -> int:
        """
        Get the next available thought ID based on existing directories.

        :return: Next available thought ID as an integer.
        """
        os.makedirs(FileManagement.thoughts_folder, exist_ok=True)
        return len([name for name in os.listdir(FileManagement.thoughts_folder) if
                    os.path.isdir(os.path.join(FileManagement.thoughts_folder, name))]) + 1

    @staticmethod
    def _get_file_path(file_name: str) -> str:
        """Get the full path for a file in the given thought and file name.

        :param file_name: The name of the file.
        :return: The full path of the file.
        """
        return os.path.join(FileManagement.thoughts_folder, str(Globals.thought_id), file_name)

    @staticmethod
    def _get_thought_folder(thought_id: str) -> str:
        """Get the folder path for a given thought ID.

        :param thought_id: The ID of the currently executing thought.
        :return: The folder path for the given thought ID.
        """
        return os.path.join(FileManagement.thoughts_folder, thought_id)


if __name__ == '__main__':
    # FileManagement.re_write_section("""Generate a response based on system and user prompts.
    #                                 """, "womp", "thought.py", "1")

    FileManagement.save_file("Test", "test_test")
