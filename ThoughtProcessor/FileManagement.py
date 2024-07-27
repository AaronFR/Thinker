import os
import logging

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
            logging.error(f"ERROR: could not save instantiate file: {file_path}\n {str(e)} \nThought_id: {thought_id}")

    @staticmethod
    def save_to_solution(content: str, thought_id: str):
        """Append content to the solution.txt file for a given thought."""
        file_path = f"Thoughts/{thought_id}/solution.txt"
        try:
            logging.info(f"{thought_id}: Attempting to save solution")
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(content + "\n")
                logging.info(f"Solution saved for thought_id: {thought_id}")
        except Exception as e:
            logging.error(f"ERROR: could not save file, {str(e)} \n Thought_id: {thought_id}")

    @staticmethod
    def read_solution(thought_id: str) -> str:
        """Read a given solution.txt file for a given thought id number."""
        file_path = f"Thoughts/{thought_id}/solution.txt"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logging.error(f"ERROR: could not read file, {str(e)}")
            return "[FATAL ERROR COULD NOT READ SOLUTION]"