import logging
from typing import List, Tuple

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Functionality.Coding import Coding
from Functionality.Organising import Organising
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import PersonaConstants, CoderSpecification
from Utilities.Utility import Utility


class Coder(BasePersona):
    """
    Thinker persona to facilitate conversational interactions
    """
    MAX_HISTORY = 5

    def __init__(self, name):
        super().__init__(name)
        self.history: List[Tuple[str, str]] = []  # question-response pairs

    def think(self, user_messages: List[str]) -> str:
        """Process the input question and think through a response.

        :param user_messages: List of existing user message
        :return The generated response or error message
        """
        logging.info("Processing user messages: %s", user_messages)

        selected_files = Organising.get_relevant_files(user_messages)
        executor = AiOrchestrator(selected_files)

        # ToDo: How the application accesses and gives history to the llm will need to be optimised
        recent_history = [entry[1] for entry in self.history[-self.MAX_HISTORY:]]

        try:
            output = executor.execute(
                [CoderSpecification.CODER_INSTRUCTIONS, CoderSpecification.load_configuration()],
                user_messages,
                assistant_messages=recent_history
            )
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

        return output

    def query_user_for_input(self):
        """Continuously prompts the user for questions until they choose to exit. """
        while True:
            new_question = input("Please enter your coding task (or type 'exit' to quit): ")
            if Utility.is_exit_command(new_question):
                print("Exiting the question loop.")
                break
            elif new_question.lower() == 'history':
                self.display_history()
            elif Utility.is_valid_question(new_question):
                self.run_workflow(new_question)
            else:
                print("Invalid input. Please ask a clear and valid question.")

    def display_history(self):
        """Display the conversation history to the user."""
        if not self.history:
            print("No interaction history available.")
            return
        print("Interaction History:")
        for i, (question, response) in enumerate(self.history):
            print(f"{i + 1}: Q: {question}\n    A: {response}")

    def process_question(self, question: str):
        """Process and store the user's question."""
        response = self.think([question])
        self.history.append((question, response))
        return response

    def run_workflow(self, initial_message: str):
        """Engage in a back-and-forth dialogue with itself."""
        executor = AiOrchestrator()
        new_file = executor.execute(
            "Give just a filename (with extension) that should be worked on given the following prompt. No commentary",
            initial_message)

        analyser_messages = [
            f"Examine the current implementation of {new_file} and your answer for any logical inconsistencies or flaws. Identify specific areas where the logic might fail or where the implementation does not meet the requirements. Provide a revised version addressing these issues.",
            f"Evaluate the current implementation of {new_file} for opportunities to enhance features, improve naming conventions, and increase documentation clarity. Assess readability and flexibility. Provide a revised version that incorporates these improvements.",
            f"Review the structure and flow of the documentation in {new_file}. Suggest and implement changes to improve the organization, clarity, and ease of understanding of the documentation. Provide a revised version with these changes.",
            f"Present the final revised version of the code in {new_file}, incorporating all previous improvements we discussed. Additionally, provide a summary of the key changes made, explaining how each change enhances the code."
        ]

        prompt_messages = [initial_message] + analyser_messages
        for iteration, message in enumerate(prompt_messages):
            response = self.process_question(message)
            logging.info("Iteration %d completed with response: %s", iteration, response)

            if iteration == 4:
                Coding.write_to_file_task({
                    PersonaConstants.SAVE_TO: new_file,
                    PersonaConstants.INSTRUCTION: response
                })


if __name__ == '__main__':
    coder = Coder("proto")
    coder.query_user_for_input()
    # thinker.self_converse("How would you improve the Thinker.py class")
