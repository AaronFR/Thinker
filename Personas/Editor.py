import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Writing import Writing
from Personas.PersonaSpecification import PersonaConstants, EditorSpecification
from Utilities.ErrorHandler import ErrorHandler
from Personas.BasePersona import BasePersona


class Editor(BasePersona):
    """
    Editor persona is responsible for editorialising: reviewing an existing document and making substitutions and
    amendments.
    """

    def __init__(self, name):
        super().__init__(name)
        self.workflows = {
            "re_write": "Workflow for editorialising and rewriting a file"
        }
        self.instructions = EditorSpecification.EDITOR_INSTRUCTIONS
        self.configuration = EditorSpecification.load_configuration()

        ErrorHandler.setup_logging()

    def run_workflow(self, selection: str, initial_message: str):
        if selection in self.workflows.keys():
            if selection == "re_write":
                self.re_write_workflow(initial_message)

    def re_write_workflow(self, initial_message: str):
        """Engage in a back-and-forth dialogue with itself, with the aim of re-writing a document."""
        executor = AiOrchestrator()
        file_name = executor.execute(
            "Give just a filename (with extension) that should be worked on given the following prompt. No commentary",
            initial_message)

        # Should decide whether to rewrite individual lines or rewrite the entire document

        analyser_messages = [
            f"Examine the current implementation of {file_name} and your answer for any logical inconsistencies or flaws. Identify specific areas where the logic might fail or where the implementation does not meet the requirements. Provide a revised version addressing these issues.",
            f"Evaluate the current implementation of {file_name} for opportunities to enhance features, improve naming conventions, and increase documentation clarity. Assess readability and flexibility. Provide a revised version that incorporates these improvements.",
            f"Review the structure and flow of the documentation in {file_name}. Suggest and implement changes to improve the organization, clarity, and ease of understanding of the code and its documentation. Provide a new and improved version of the code with its improved documentation.",
            f"Present the final revised version of the code in {file_name}, incorporating all previous improvements we discussed. Additionally, provide a summary of the key changes made, explaining how each change enhances the code."
        ]

        # Should have a task evaluating if there are any terms to regex rewrite globally.

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
    - Review the translated report for structural coherence according to Dutch reporting styles.
     Organize the information with clear headings and sections, including an inleiding (introduction) and conclusie (conclusion).
     Ensure that the formatting aligns with typical Dutch standards for academic or historical reports.
    - Alter the docstring for each method present. Focus, laser focus, on readability.
    """

    editor = Editor("prototype")
    editor.query_user_for_input()
