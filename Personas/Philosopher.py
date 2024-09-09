import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Coding import Coding
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, CoderSpecification


class Philosopher(BasePersona):
    """
    Philosopher persona for discussing interesting philosophical ideas
    """

    def __init__(self, name):
        """
        Initialize the Philosopher persona with a given name.

        :param name: The name of the philosopher persona.
        """
        super().__init__(name)
        self.workflows = {
            "write": "Workflow for writing a general consideration of a given topic"
        }
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()

    def run_workflow(self, selected_workflow: str, initial_message: str):
        if selected_workflow in self.workflows.keys():
            if selected_workflow == "write":
                self.write_workflow(initial_message)

    def write_workflow(self, initial_message: str):
        """
        Writes the response to a given idea

        :param initial_message: The user's initial guidance for writing the response.
        """
        executor = AiOrchestrator()
        file_name = executor.execute(
            ["Give just a filename (with extension) that should be worked on given the following prompt. No commentary"],
            [initial_message])

        # ToDo: Would be a strong contender for 'prompt optimisation'
        analyser_messages = [
            f"{initial_message}: Put another way -> Explain the philosophical discussion about the subject in a way "
            "that feels natural and engaging, without resorting to forced dramatization. Make it intellectually "
            "stimulating but authentic."
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

    philosopher = Philosopher("prototype")
    philosopher.query_user_for_input()
