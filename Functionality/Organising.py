import logging
from typing import List, Tuple

from deprecated import deprecated

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.ThinkerSpecification import SELECT_FILES_FUNCTION_SCHEMA
from Data.FileManagement import FileManagement


class Organising:

    @deprecated(reason="ToDo adapt for node graph system")
    @staticmethod
    def get_relevant_files(input: List[str]) -> List[str]:
        """Retrieves relevant files based on the input question.

        ToDo Optimisation, including a quick check to filter if a question should *even* be referencing other files and
         if so which files should it even read the summary of

        :param input: A list of input questions
        :return A list of selected file names that are deemed relevant to the input questions
        """
        logging.info("GET_RELEVANT_FILES triggered")
        evaluation_files = FileManagement.list_staged_files()  # needs to be changed to find files from ALL categories
        if not evaluation_files:
            logging.warning("No evaluation files found.")
            return []

        Organising.summarise_files(evaluation_files)
        summaries = Organising.get_files_with_summary()

        executor = AiOrchestrator()
        try:
            output = executor.execute_function(
                [Organising._build_file_query_prompt(summaries)],
                input,
                SELECT_FILES_FUNCTION_SCHEMA
            )
            selected_files = output.get('files', [])

            logging.info(f"Selected: {selected_files}, \nfrom: {evaluation_files}")

            selected_files = FileManagement.list_staged_files()  # defaulting to grabbing staged files
            logging.info(f"Selected files: {selected_files}")
            return selected_files
        except Exception as e:
            logging.exception("Error retrieving relevant files", e)
            return []

    @deprecated()
    @staticmethod
    def _build_file_query_prompt(evaluation_files: Tuple[str, str]) -> str:
        """Construct the prompt for selecting relevant files."""
        file_name_and_summary = ""
        for file_name, file_summary in evaluation_files:
            file_name_and_summary += f"\n{file_name} Summary: {file_summary}"

        return f"""From the list of files, choose which files are expressively explicitly relevant to my prompt. 
        This could be one, many, or NO files. Be cautious about including files.
        files: {evaluation_files}"""

    @staticmethod
    def summarise_content(content: str):
        """Creates and saves a summary file for the given file.
        ToDo: should use AST for coding files - when we create 'structure' methods

        :param content: The content to be summarised
        """
        executor = AiOrchestrator()
        summary = executor.execute(
            [PersonaConstants.SUMMARISER_SYSTEM_INSTRUCTIONS],
            [content]
        )
        return summary


if __name__ == '__main__':
    parent_class_name = "EncyclopediaManagementInterface.py"
    child_class_name = "UserEncyclopediaMangement.py"
    Organising.get_relevant_files(
        [f"Hey can you compare {parent_class_name} and the child class {child_class_name}?"]
    )
