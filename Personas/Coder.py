import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Coding import Coding
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, CoderSpecification


class Coder(BasePersona):
    """
    Coding persona to write and edit coed files.
    """

    def __init__(self, name):
        super().__init__(name)
        self.workflows = {
            "write": "Workflow for creating or overwriting a code file"
        }
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()

    def write_workflow(self, initial_message: str):
        """Engage in a back-and-forth dialogue with itself, with the aim of writing a document."""
        executor = AiOrchestrator()
        file_name = executor.execute(
            "Give just a filename (with extension) that should be worked on given the following prompt. No commentary",
            initial_message)

        analyser_messages = [
            f"Examine the current implementation of {file_name} and your answer for any logical inconsistencies or flaws. Identify specific areas where the logic might fail or where the implementation does not meet the requirements. Provide a revised version addressing these issues.",
            f"Evaluate the current implementation of {file_name} for opportunities to enhance features, improve naming conventions, and increase documentation clarity. Assess readability and flexibility. Provide a revised version that incorporates these improvements.",
            f"Review the structure and flow of the documentation in {file_name}. Suggest and implement changes to improve the organization, clarity, and ease of understanding of the code and its documentation. Provide a new and improved version of the code with its improved documentation.",
            f"Present the final revised version of the code in {file_name}, incorporating all previous improvements we discussed. Additionally, provide a summary of the key changes made, explaining how each change enhances the code."
        ]

        prompt_messages = [initial_message] + analyser_messages
        for iteration, message in enumerate(prompt_messages):
            response = self.process_question(message)
            logging.info("Iteration %d completed with response: %s", iteration, response)

            if iteration == 4:
                Coding.write_to_file_task({
                    PersonaConstants.SAVE_TO: file_name,
                    PersonaConstants.INSTRUCTION: response
                })


if __name__ == '__main__':
    """Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain, 
     assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """

    coder = Coder("prototype")
    coder.query_user_for_input()
