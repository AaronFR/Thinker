import logging
from typing import Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Coding import Coding
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, CoderSpecification
from Personas.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA
from Utilities.Utility import Utility


class Coder(BasePersona):
    """
    Coding persona to write and edit code files.
    """

    def __init__(self, name):
        """
        Initialize the Coder persona with a given name.

        :param name: The name of the coding persona.
        """
        super().__init__(name)
        self.workflows = {
            "chat": "Discuss code/coding with the user",
            "write": "Workflow for creating or overwriting a code file",
            "write_tests": "Workflow for creating or overwriting a coding test file"
        }
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()

    def run_workflow(self, selected_workflow: str, initial_message: str):
        if selected_workflow in self.workflows.keys():
            if selected_workflow == "chat":
                self.chat_workflow(initial_message)
            if selected_workflow == "write":
                self.write_workflow(initial_message)
            if selected_workflow == "write_tests":
                self.write_tests_workflow(initial_message)

    def chat_workflow(self, initial_message: str):
        """
        Converses with the user

        :param initial_message: The user's initial prompt.
        """
        analyser_messages = [
            initial_message
        ]
        prompt_messages = analyser_messages

        try:
            for iteration, message in enumerate(prompt_messages):
                response = self.process_question(message)
                logging.info("Iteration %d completed with response: %s", iteration, response)

        except Exception as e:
            logging.exception("Error during writing workflow: %s", str(e), exc_info=e)

    def write_workflow(self, initial_message: str):
        """
        Writes the improved code to a specified file.

        :param initial_message: The user's initial guidance for writing the code.
        """
        executor = AiOrchestrator()
        files = executor.execute_function(
            ["Give just a filename (with extension) that should be worked on given the following prompt. No commentary."
             "If appropriate write multiple files, the ones at the top of the class hierarchy first/ on the top"],
            [initial_message],
            GENERATE_FILE_NAMES_FUNCTION_SCHEMA
        )['files']
        logging.info(f"Referencing/Creating the following files: {files}")

        for file in files:
            file_name = file['file_name']
            purpose = file['purpose']
            logging.info(f"Writing code to {file_name}")

            if Coding.is_coding_file(file_name):
                step_two = f"Write/Rewrite {file_name} based on your comments, focusing on addressing " \
                           f"[{purpose}] as well as possible."
            else:
                step_two = f"Write/Rewrite {file_name} based on your comments, focusing on addressing " \
                           f"[{purpose}] as well as possible. Making sure that the file imports as necessary, " \
                           "referencing the appropriate classes"

            analyser_messages = [
                f"{initial_message}: We will focus on {file_name} so as to {purpose}, to start with think through the"
                "proposed problem step by step, discuss what we now, what we want to accomplish, the goals and subgoals"
                " we should optimise for, and any existing flaws to address in the file if it exists yet."
                "Add a authros note Re the thinker",

                step_two
            ]
            prompt_messages = analyser_messages

            try:
                for iteration, message in enumerate(prompt_messages, start=1):
                    response = self.process_question(message)
                    logging.info("Iteration %d completed with response: %s", iteration, response)

                    if iteration == len(prompt_messages):
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
            ["Please provide the filename (including extension) of the code for which tests should be written. "
            "Please be concise."],
            [initial_message]
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
