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
        """
        Initialize the Coder persona with a given name.

        :param name: The name of the coding persona.
        """
        super().__init__(name)
        self.workflows = {
            "write": "Workflow for creating or overwriting a code file",
            "write_tests": "Workflow for creating or overwriting a coding test file"
        }
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()

    def write_workflow(self, initial_message: str):
        """
        Writes the improved code to a specified file.

        :param initial_message: The user's initial guidance for writing the code.
        """
        executor = AiOrchestrator()
        file_name = executor.execute(
            "Give just a filename (with extension) that should be worked on given the following prompt. No commentary",
            initial_message)

        analyser_messages = [
            f"Examine the current implementation of {file_name} and your answer for any logical inconsistencies or "
            "flaws. Identify specific areas where the logic might fail or where the implementation does not meet "
            "the requirements. Provide a revised version addressing these issues.",
            f"Evaluate the current implementation of {file_name} for opportunities to enhance features, improve naming "
            "conventions, and increase documentation clarity. Assess readability and flexibility. "
            "Provide a revised version that incorporates these improvements.",
            f"Review the structure and flow of the documentation in {file_name}. "
            "Suggest and implement changes to improve the organization, clarity, and ease of understanding of the code "
            "and its documentation. Provide a new and improved version of the code with its improved documentation.",
            f"Assess the code in {file_name} for adherence to coding standards and best practices. "
            "Suggest changes to improve code quality.",
            f"Present the final revised version of the code in {file_name}, "
            "incorporating all previous improvements we discussed. "
            "Additionally, provide a summary of the key changes made, explaining how each change enhances the code."
        ]
        prompt_messages = [initial_message] + analyser_messages

        try:
            for iteration, message in enumerate(prompt_messages):
                response = self.process_question(message)
                logging.info("Iteration %d completed with response: %s", iteration, response)

                if iteration == 5:
                    Coding.write_to_file_task({
                        PersonaConstants.SAVE_TO: file_name,
                        PersonaConstants.INSTRUCTION: response
                    })

        except Exception as e:
            logging.error("Error during writing workflow: %s", str(e))

    def write_tests_workflow(self, initial_message: str) -> None:
        """
        Generates a test file for a specified file

        :param initial_message: The user's initial guidance for writing tests.
        """
        executor = AiOrchestrator()
        file_name = executor.execute(
            "Please provide the filename (including extension) of the code for which tests should be written. Please be concise.",
            initial_message
        )

        test_prompt_messages = [
            f"Create unit tests for the functionality provided in {file_name}. Ensure all major functions are tested.",
            f"Assess edge cases and boundary conditions in {file_name}, generating appropriate tests.",
            f"Generate tests that ensure robust error handling in the functions defined in {file_name}.",
            f"Compile the unit tests generated into one cohesive test suite for {file_name}.",
            f"Present the final test cases in {file_name} and comment on coverage and areas needing additional tests."
        ]
        prompt_messages = [initial_message] + test_prompt_messages

        try:
            for iteration, message in enumerate(prompt_messages):
                response = self.process_question(message)
                logging.info("Test Workflow Iteration %d completed with response: %s", iteration, response)

                # Save the response after the last message
                if iteration == len(prompt_messages) - 1:
                    Coding.write_to_file_task({
                        PersonaConstants.SAVE_TO: file_name,
                        PersonaConstants.INSTRUCTION: response
                    })

        except Exception as e:
            logging.error("Error during writing tests workflow: %s", str(e))

if __name__ == '__main__':
    """Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain, 
     assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """

    coder = Coder("prototype")
    coder.query_user_for_input()
