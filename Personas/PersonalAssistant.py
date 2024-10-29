import logging
from typing import List

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Writing import Writing
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, PersonalAssistantSpecification as PaSpecification
from Personas.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA


class PersonalAssistant(BasePersona):
    """
    Personal Assistant persona for helping the user organise

    Because 'assistant' is already a term in the ChatGpt API, and we do not need that confusion
    """

    def __init__(self, name):
        """
        Initialize the PersonalAssistant persona with a given name.

        :param name: The name of the PA persona.
        """
        super().__init__(name)
        self.workflows = {
            "chat": "Just converse with the user naturally",
            "write": "Workflow for writing an organised note to be given to the user"
        }
        self.instructions = PaSpecification.PERSONAL_ASSISTANT_INSTRUCTIONS
        self.configuration = PaSpecification.load_configuration()

    def run_workflow(self,
                     user_id: str,
                     selected_workflow: str,
                     initial_message: str,
                     file_references: List[str] = None):
        if selected_workflow in self.workflows.keys():
            if selected_workflow == "chat":
                self.chat_workflow(user_id, initial_message)
            if selected_workflow == "write":
                self.write_workflow(user_id, initial_message)

    def chat_workflow(self, user_id: str, initial_message: str):
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
                response = self.process_question(user_id, message)
                logging.info("Iteration %d completed with response: %s", iteration, response)

        except Exception as e:
            logging.error("Error during writing workflow: %s", str(e))

    def write_workflow(self, user_id: str, initial_message: str):
        """
        Writes the response to a give user request

        :param initial_message: The user's initial guidance for writing the response.
        """
        executor = AiOrchestrator()
        files = executor.execute_function(
            ["Give just a filename (with extension) that should be worked on given the following prompt. No commentary"
             "The user will point files out, reference files will be used elsewhere, write to the file(s) they "
             "suggest"],
            [initial_message],
            GENERATE_FILE_NAMES_FUNCTION_SCHEMA
        )['files']
        logging.info(f"Referencing/Creating the following files: {files}")

        # ToDo: Would be a strong contender for 'prompt optimisation'
        analyser_messages = [
            f"{initial_message}: Now write that to an organised file, DO NOT COMMENT, just re/write the file"
        ]
        prompt_messages = analyser_messages

        for file in files:
            file_name = file['file_name']
            purpose = file['purpose']
            logging.info(f"PA writing to {file_name}, \nPurpose: {purpose}")

            try:
                for iteration, message in enumerate(prompt_messages, start=1):
                    response = self.process_question(user_id, message)
                    logging.info("Iteration %d completed with response: %s", iteration, response)

                    if iteration == len(prompt_messages):
                        Writing.write_to_file_task({  #
                            PersonaConstants.SAVE_TO: file_name,
                            PersonaConstants.INSTRUCTION: response
                        })
            except Exception as e:
                logging.error("Error during writing workflow: %s", str(e))


if __name__ == '__main__':
    """Suggestions:
    - 
    """

    personalAssistant = PersonalAssistant("PA")
    personalAssistant.query_user_for_input()
