import logging
import os
from typing import List, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import ThinkerSpecification, SummariserSpecification
from Personas.PersonaSpecification.ThinkerSpecification import SELECT_FILES_FUNCTION_SCHEMA
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.FileManagement import FileManagement


class Organising:

    @staticmethod
    def get_relevant_files(input: List[str]) -> List[str]:
        """Retrieves relevant files based on the input question.

        :param input: A list of input questions
        :return A list of selected file names that are deemed relevant to the input questions
        """
        evaluation_files = FileManagement.list_file_names()
        if not evaluation_files:
            logging.warning("No evaluation files found.")
            return []

        Organising.summarise_files(evaluation_files)
        summaries = Organising.get_files_with_summary()

        executor = AiOrchestrator()
        try:
            output = executor.execute_function(
                [ThinkerSpecification.build_file_query_prompt(summaries)],
                input,
                SELECT_FILES_FUNCTION_SCHEMA
            )
            selected_files = output.get('files', [])

            logging.info(f"Selected: {selected_files}, \nfrom: {evaluation_files}")
            return selected_files
        except Exception as e:
            logging.exception("Error retrieving relevant files", e)
            return []

    @staticmethod
    def get_files_with_summary() -> Tuple[str, str]:
        """
        :return: A tuple of files and their summary counterparts
        """
        files_with_summary = ()
        evaluation_files = FileManagement.list_file_names()
        evaluation_files_set = set(evaluation_files)

        regular_files_set = {file_name for file_name in evaluation_files if not file_name.endswith("_summary.txt")}

        # Identify summary files first
        for file in regular_files_set:
            name_parts = file.rsplit('.', 1)
            if len(name_parts) == 1:
                logging.warning("File without file extension")
                name_parts.append("txt")

            summary_file_name = f"{name_parts[0]}_summary.txt"

            if summary_file_name in evaluation_files_set:
                files_with_summary += ((file, summary_file_name),)

        return files_with_summary

    @staticmethod
    def summarise_files(evaluation_files: List[str]):
        """Creates summaries for any file that does not have an associated summary.

        :param evaluation_files: A list of evaluation files to be potentially summarised
        """
        summary_files = set()
        evaluation_files_set = set(evaluation_files)
        regular_files_set = {file for file in evaluation_files if not file.endswith("_summary.txt")}

        for file_name in regular_files_set:
            name_parts = file_name.rsplit('.', 1)
            if len(name_parts) == 1:
                logging.warning("File without file extension")
                name_parts = [name_parts, "txt"]

            summary_file_name = f"{name_parts[0]}_summary.{name_parts[1]}"

            if summary_file_name in evaluation_files_set:
                summary_files.add(file_name)

        for file_name in regular_files_set:
            if file_name not in summary_files:
                Organising.create_summary_file(file_name)

    @staticmethod
    def create_summary_file(file: str):
        """Creates and saves a summary file for the given file.

        :param file: The original file for which a summary will be created
        """
        summary = Organising.summarise_file(file)

        summary_filename = Organising.create_summary_filename(file)
        FileManagement.save_file(summary, summary_filename, overwrite=True)
        ExecutionLogs.add_to_logs(f"Summariser: Summary for {file} written and saved as {summary_filename}")

    @staticmethod
    def create_summary_filename(original_filename: str) -> str:
        """Creates a summary file name based on the original file name.

        :param original_filename: The name of the original file
        :return: A string representing the summary file name
        """
        base, _ = os.path.splitext(original_filename)
        return f"{base}_summary.txt"

    @staticmethod
    def summarise_file(file_name: str) -> str:
        """Generates a summary text for the given file.

        :param file_name: The original file text that needs to be summarized
        :return: A string containing the summary of the file
        """
        content = FileManagement.read_file(file_name)
        executor = AiOrchestrator()

        summary = executor.execute(
            [SummariserSpecification.SUMMARISER_SYSTEM_INSTRUCTIONS],
            [f"Please summarize the content I previously gave you", content]
        )

        return summary
