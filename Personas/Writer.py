import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Writing import Writing
from Utilities.ErrorHandler import ErrorHandler
from Personas.PersonaSpecification import PersonaConstants, WriterSpecification
from Personas.BasePersona import BasePersona
from Data.FileManagement import FileManagement


class Writer(BasePersona):
    """
    Writer persona, representing a role that manages writing tasks and their outputs

    This persona handles tasks such as creating new documents or appending to existing files.
    """

    def __init__(self, name):
        super().__init__(name)
        self.workflows = {
            "write": "Workflow for creating or overwriting a text document"
        }
        self.instructions = WriterSpecification.WRITER_INSTRUCTIONS
        self.configuration = WriterSpecification.load_configuration()

        ErrorHandler.setup_logging()

    def run_workflow(self, selected_workflow: str, initial_message: str):
        if selected_workflow in self.workflows.keys():
            if selected_workflow == "write":
                self.write_workflow(initial_message)

    def write_workflow(self, initial_message: str):
        """Engage in a back-and-forth dialogue with itself, with the aim of writing a document."""
        executor = AiOrchestrator()
        file_name = executor.execute(
            ["Give just a filename (with extension) that should be worked on given the following prompt. No commentary"],
            [initial_message])

        evaluation_files = FileManagement.list_file_names()
        if file_name in evaluation_files:
            file_name = executor.execute(
                ["Given the context of the following prompt, should the writing be appended or should it overwrite "
                "the file? No commentary"],
                [initial_message])
        # Decide if new text should be appended to a document. (why and when??)

        analyser_messages = [
            f"Examine the current implementation of {file_name} and your answer for any logical inconsistencies or "
            "flaws. Identify specific areas where the logic might fail or where the implementation does not meet the "
            "requirements. Provide a revised version addressing these issues.",
            f"Evaluate the current implementation of {file_name} for opportunities to enhance features, improve naming "
            "conventions, and increase documentation clarity. Assess readability and flexibility. Provide a revised "
            "version that incorporates these improvements.",
            f"Review the structure and flow of the documentation in {file_name}. Suggest and implement changes to "
            "improve the organization, clarity, and ease of understanding of the code and its documentation. Provide a "
            "new and improved version of the code with its improved documentation.",
            f"Present the final revised version of the code in {file_name}, incorporating all previous improvements we "
            "discussed. Additionally, provide a summary of the key changes made, "
            "explaining how each change enhances the text."
        ]

        prompt_messages = [initial_message] + analyser_messages
        for iteration, message in enumerate(prompt_messages):
            response = self.process_question(message)
            logging.info("Iteration %d completed with response: %s", iteration, response)

            if iteration == 4:
                Writing.write_to_file({
                    PersonaConstants.SAVE_TO: file_name,
                    PersonaConstants.INSTRUCTION: response
                })


if __name__ == '__main__':
    """Suggestions: 
    - Write a detailed report about the future of tidal technology, what innovations and possible disruptions could occur
    """

    writer = Writer("prototype")
    writer.query_user_for_input()
