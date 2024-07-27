import logging
from datetime import datetime

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pathlib import Path

from typing_extensions import deprecated


class FileProcessing:

    def __init__(self, output_directory='output_html_files', style='colorful'):
        self.output_directory = Path(output_directory)
        self.style = style
        self.output_directory.mkdir(exist_ok=True)  # Create directory if it does not exist

    def format_to_html(self, text: str) -> str:
        """
        Formats the provided text as HTML.
        :param text: Initial text with format characters e.g. \n
        :return: HTML formatted string of the input text.
        """
        html_formatter = HtmlFormatter(full=True, style=self.style)
        highlighted_code = highlight(text, PythonLexer(), html_formatter)
        return highlighted_code

    def save_as_html(self, content: str, file_name: str, prompt_id: str):
        """
        Saves the response content in HTML format to a file.

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the output HTML file.
        :param prompt_id: An identifier to make the file name unique.
        """
        html_text = self.format_to_html(content)
        file_path = self.output_directory / f"{file_name}_{prompt_id}.html"

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_text)
        except Exception as e:
            logging.error(f"ERROR: could not save file, {str(e)}")

    @staticmethod
    def save_as_text(content: str, file_name, prompt_id: str):
        """
        Saves the response content in HTML format to a file.
        Very similar to save_file which replaces this method

        :param content: The content to be formatted and saved.
        :param file_name: The base name for the output HTML file.
        :param prompt_id: An identifier to make the file name unique.
        """
        file_path = f"{file_name}_{prompt_id}.txt"
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
                logging.debug("File Saved: {file_path}")
        except Exception as e:
            logging.error(f"ERROR: could not save file, {str(e)}")

    def aggregate_files(self, file_base_name, start, end):
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
                    print(f"CONTENT [{i}]: {content}")
                except FileNotFoundError:
                    logging.error(f"File {file_base_name + '_' + str(i) + '.txt'} not found.")
                except UnicodeDecodeError as e:
                    logging.error(f"Error decoding file {file_base_name + '_' + str(i) + '.txt'}: {e}")
                except Exception as e:
                    logging.error(f"ERROR: could not save file, {str(e)}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.save_as_html(content, "solution", timestamp)
        self.save_as_text(content, "solution", timestamp)


if __name__ == '__main__':
    html_processing = FileProcessing()
    # html_processing.save_as_text("EXAMPLE", "Task", 1)
    html_processing.aggregate_files("Task", 1, 18)
