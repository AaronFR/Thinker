import os
import logging
from typing import List


class FileManagement:
    @staticmethod
    def initialise_file(thought_id: int, file: str):
        """Initialise the solution.txt file."""
        os.makedirs(f"Thoughts/{thought_id}", exist_ok=True)
        file_path = os.path.join("Thoughts", str(thought_id), file)
        try:
            with open(file_path, "w", encoding="utf-8"):
                logging.info(f"File {file_path} instantiated.")
        except Exception as e:
            logging.error(f"ERROR: could not instantiate file: {file_path}\n {str(e)} \nThought_id: {thought_id}")

    @staticmethod
    def read_file(file_path: str) -> str:
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
        contents = []
        for path in file_paths:
            logging.info(f"Attempting to access {path}")
            contents.append(FileManagement.read_file(path))
        return contents

    @staticmethod
    def read_solution(thought_id: str) -> str:
        """Read a given solution.txt file for a given thought ID."""
        file_path = os.path.join("Thoughts", thought_id, "solution.txt")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"ERROR: File not found: {file_path}")
            return "[FATAL ERROR: COULD NOT FIND SOLUTION FILE]"
        except Exception as e:
            logging.error(f"ERROR: could not read file, {str(e)}")
            return "[FATAL ERROR: COULD NOT READ SOLUTION]"

    @staticmethod
    def save_to_solution(content: str, thought_id: str):
        """Append content to the solution.txt file for a given thought."""
        file_path = os.path.join("Thoughts", thought_id, "solution.txt")
        try:
            logging.info(f"{thought_id}: Attempting to save solution")
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(content + "\n")
                logging.info(f"Solution saved for thought_id: {thought_id}")
        except Exception as e:
            logging.error(f"Could not save file, {str(e)} \nThought_id: {thought_id}")

