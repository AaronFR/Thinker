import os

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
            summary = self.summarize_file(file)
            # Save the summary into the summaries directory, with the same name but a different extension or suffix
            summary_filename = self.create_summary_filename(file)
            FileManagement.save_file(summary, summary_filename, overwrite=True)
            ExecutionLogs.add_to_logs(f"Summariser: Summary for {file} written and saved as {summary_filename}")

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


if __name__ == '__main__':
    testSummariser = Summariser("test")
    testSummariser.execute_task("Analyst.py")