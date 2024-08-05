import os
import logging
import re
from typing import List
from datetime import datetime
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from ThoughtProcessor.ErrorHandler import ErrorHandler


class FileManagement:
    """Class for managing files related to tasks and solutions."""

    def __init__(self):
        ErrorHandler.setup_logging()

        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")

    @staticmethod
    def initialise_file(thought_id: int, file: str):
        """Initialize a given file as an empty file, in advance of it being opened
        instance declarations, doesn't make sense.

        :param thought_id: The ID of the currently executing thought.
        :param file: The name of the file to initialize.
        """
        os.makedirs(f"thoughts/{thought_id}", exist_ok=True)
        file_path = os.path.join("thoughts", str(thought_id), file)
        try:
            with open(file_path, "w", encoding="utf-8"):
                logging.info(f"File {file_path} instantiated.")
        except Exception as e:
            logging.error(f"ERROR: could not instantiate file: {file_path}\n {str(e)} \nThought_id: {thought_id}")

    @staticmethod
    def list_files(thoughts_id: str="1") -> list:
        """
        List all file names in the given directory.

        :param file_name: The path to the directory.
        :return: A list of file names in the directory.
        """
        thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts", thoughts_id)
        try:
            entries = os.listdir(thoughts_folder)
            file_names = [entry for entry in entries if os.path.isfile(os.path.join(thoughts_folder, entry))]
            logging.info(f"Found the following files in Thought space: {file_names}")

            return file_names
        except FileNotFoundError:
            logging.error(f"The directory {thoughts_folder} does not exist.")
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
        full_path = os.path.join("thoughts", "1", file_path)
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
        dir_path = os.path.join("thoughts", str(thought_id))
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join("thoughts", str(thought_id), file_name)
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
            file_path = os.path.join("thoughts", thought_id, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_text)
                logging.info(f"File overwritten: {file_path}")
        except Exception as e:
            logging.error(f"could not save file, {str(e)}")

    def save_as_html(self, content: str, file_name: str, prompt_id: str):
        """
        Saves the response content in HTML format to a file.

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the output HTML file.
        :param prompt_id: An identifier to make the file name unique.
        """
        dir_path = os.path.join("thoughts", str(prompt_id))
        os.makedirs(dir_path, exist_ok=True)

        html_text = self.format_to_html(content)
        file_path = dir_path + f"/{file_name}_{prompt_id}.html"

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_text)
        except Exception as e:
            logging.error(f"ERROR: could not save file, {str(e)}")

    def format_to_html(self, text: str) -> str:
        """
        Formats the provided text as HTML.
        :param text: Initial text with format characters e.g. \n
        :return: HTML formatted string of the input text.
        """
        html_formatter = HtmlFormatter(full=True, style=self.style)
        highlighted_code = highlight(text, PythonLexer(), html_formatter)
        return highlighted_code

    def aggregate_files(self, file_base_name, start, end, thought_id=1):
        i = start - 1
        end -= 1
        content = ""

        if end >= i > -1:
            while i <= end:
                i += 1
                try:
                    with open(file_base_name + "_" + str(i) + ".txt", 'r', encoding='utf-8') as f:
                        # Read content from each output file and write it to the consolidated file
                        content += f.read()
                    logging.info(f"CONTENT [{i}]: {content}")
                except FileNotFoundError:
                    logging.error(f"File {file_base_name + '_' + str(i) + '.txt'} not found.")
                except UnicodeDecodeError as e:
                    logging.error(f"Error decoding file {file_base_name + '_' + str(i) + '.txt'}: {e}")
                except Exception as e:
                    logging.error(f"ERROR: could not save file, {str(e)}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_as_html(content, "solution", timestamp)
        FileManagement.save_file(content, "solution", str(thought_id), overwrite=True)

    @staticmethod
    def get_next_thought_id(thoughts_folder) -> int:
        """
        Get the next available thought ID based on existing directories.

        :return: Next available thought ID as an integer.
        """
        os.makedirs(thoughts_folder, exist_ok=True)
        return len([name for name in os.listdir(thoughts_folder) if
                    os.path.isdir(os.path.join(thoughts_folder, name))]) + 1


if __name__ == '__main__':
    # FileManagement.re_write_section("""Generate a response based on system and user prompts.
    #                                 """, "womp", "thought.py", "1")

    FileManagement.save_file("Test", "test_test", 1)


