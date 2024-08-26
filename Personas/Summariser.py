import logging
import os
from typing import List

from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, SummariserSpecification
from Utilities.ErrorHandler import ErrorHandler
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.FileManagement import FileManagement


class Summariser(BasePersona):

    def __init__(self, name):
        super().__init__(name)
        self.thought_directory = os.path.dirname(__file__)
        self.evaluation_files = []

        ErrorHandler.setup_logging()

    def execute_task(self, task):
        """Load files, generate summaries, and save them."""
        if task:
            evaluation_files = [task]
        else:
            evaluation_files = FileManagement.list_file_names()

        # Create summary for each file
        for file in evaluation_files:
            self.create_summary_file(file)


    def summarise_files(self, evaluation_files: List[str]):
        summary_files = set()
        evaluation_files_set = set(evaluation_files)

        regular_files_set = {file for file in evaluation_files if not file.endswith("_summary.txt")}

        # Identify summary files first
        for file in regular_files_set:
            name_parts = file.rsplit('.', 1)
            if len(name_parts) == 1:
                logging.warning("File without file extension")
                name_parts = [name_parts, "txt"]
            # Reconstruct the summary file name with the prefix before the extension
            summary_file = f"{name_parts[0]}_summary.{name_parts[1]}"

            # Add to summary_files set if it exists
            if summary_file in evaluation_files_set:
                summary_files.add(file)  # Keep track of original files that have summaries

        # Now, determine which files need summarization (i.e., those without summaries)
        for file in regular_files_set:
            if file not in summary_files:
                # File doesn't have a summary, so we should include it for summarization
                self.create_summary_file(file)

    def summarize_file(self, file_name: str) -> str:
        """Generate a summary for the given file."""
        content = FileManagement.read_file(file_name)  # Assuming there's a method to load file contents
        summarizer = self.create_ai_wrapper([file_name])

        summary = summarizer.execute(
            [SummariserSpecification.SUMMARISER_SYSTEM_INSTRUCTIONS],
            [f"Please summarize the following content: {content}"]
        )

        return summary

    def create_summary_filename(self, original_filename: str) -> str:
        """Create a new filename for the summary based on the original filename."""
        base, _ = os.path.splitext(original_filename)
        return f"{base}_summary.txt"

    def create_summary_file(self, file: str):
        """Save the summary into the summaries directory, with the same name but a different extension or suffix"""
        summary = self.summarize_file(file)

        summary_filename = self.create_summary_filename(file)
        FileManagement.save_file(summary, summary_filename, overwrite=True)
        ExecutionLogs.add_to_logs(f"Summariser: Summary for {file} written and saved as {summary_filename}")


if __name__ == '__main__':
    testSummariser = Summariser("test")
    testSummariser.execute_task("Analyst.py")