import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Coding import Coding
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, CoderSpecification


class PersonalAssistant(BasePersona):
    """
    Philosopher persona for discussing interesting philosophical ideas.

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
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()

    def run_workflow(self, selected_workflow: str, initial_message: str):
        if selected_workflow in self.workflows.keys():
            if selected_workflow == "chat":
                self.chat_workflow(initial_message)
            if selected_workflow == "write":
                self.write_workflow(initial_message)

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
            logging.error("Error during writing workflow: %s", str(e))

    def write_workflow(self, initial_message: str):
        """
        Writes the response to a give user request

        :param initial_message: The user's initial guidance for writing the response.
        """
        executor = AiOrchestrator()
        file_name = executor.execute(
            ["Give just a filename (with extension) that should be worked on given the following prompt. No commentary"],
            [initial_message])

        # ToDo: Would be a strong contender for 'prompt optimisation'
        analyser_messages = [
            f"{initial_message}: Now write that to an organised file"
        ]
        prompt_messages = analyser_messages

        try:
            for iteration, message in enumerate(prompt_messages):
                response = self.process_question(message)
                logging.info("Iteration %d completed with response: %s", iteration, response)

                if iteration == 0:
                    Coding.write_to_file_task({
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
