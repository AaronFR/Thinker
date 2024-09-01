import logging

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Coding import Coding
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, CoderSpecification

class Thinker(BasePersona):
    """
    Thinker persona to facilitate conversational interactions
    """
    MAX_HISTORY = 5

    def __init__(self, name):
        super().__init__(name)
        self.workflows = {
            "write": "Write down your thoughts"
        }
        self.instructions = "Just think through the question, step by step, prioritizing the most recent user prompt."
        self.configuration = CoderSpecification.load_configuration()  # ToDo: These should be added to their own config file

    def run_workflow(self, selection: str, initial_message: str):
        if selection in self.workflows.keys():
            if selection == "write":
                self.write_workflow(initial_message)

    def write_workflow(self, initial_message: str):
        """Engage in a back-and-forth dialogue with itself"""
        executor = AiOrchestrator()
        file_name = executor.execute(
            "Give just a filename (with extension) that should be worked on given the following prompt. No commentary",
            initial_message)

        analyser_messages = [
            f"Consider the essence of the idea before you in {file_name}. Reflect on the underlying logic and coherence. Are there inconsistencies or contradictions in the thought process? Where might the reasoning falter, and how could it be more aligned with its true purpose? Contemplate these aspects deeply and propose a way forward that resolves these tensions.",
            f"Engage with the idea in {file_name} as you would with a profound concept. Explore its structure and the connections between its elements. Are there opportunities to refine the expression of these thoughts? Could clarity, understanding, or flexibility be enhanced? Reflect on how the concept can be more fully realized and suggest improvements that bring its potential into sharper focus.",
            f"Observe the flow and organization of the thoughts presented in {file_name}. Does the narrative guide the mind smoothly, or are there areas where understanding becomes clouded? Consider how the communication of these ideas could be made more transparent, more engaging, and easier to grasp. Suggest a revised structure that enhances the clarity and impact of the message.",
            f"Now, synthesize your reflections into a coherent whole inside {file_name}. Present the refined version of the concept, incorporating all the insights gained from your observations and considerations."
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
    thinker = Thinker("proto")
    thinker.query_user_for_input()
    # thinker.self_converse("How would you improve the Thinker.py class")
