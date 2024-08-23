import logging
from typing import List, Tuple

from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import ThinkerSpecification
from Personas.PersonaSpecification.ThinkerSpecification import SELECT_FILES_FUNCTION_SCHEMA
from Personas.Summariser import Summariser
from Utilities.FileManagement import FileManagement
from Utilities.Utility import Utility


class Thinker(BasePersona):
    """
    Thinker persona to facilitate conversational interactions
    """
    MAX_HISTORY = 5

    def __init__(self, name):
        super().__init__(name)
        self.history: List[Tuple[str, str]] = []  # To maintain question-response pairs

    def think(self, user_messages: List[str]) -> str:
        """Process the input question and think through a response.

        :param: input: List of existing user messagse"""
        logging.info("Thinking through the input: %s", user_messages)
        try:
            selected_files = self.get_relevant_files(user_messages)
            executor = BasePersona.create_ai_wrapper(selected_files)

            #ToDo: How the application accesses and gives history to the llm will need to be optimised
            recent_history = [entry[1] for entry in self.history[-self.MAX_HISTORY:]]
            output = executor.execute(
                ["Just think through the question, step by step, prioritizing the most recent user prompt."],
                user_messages,
                assistant_messages=recent_history
            )
        except Exception as e:
            logging.exception("An error occurred while thinking: %s", e)
            return f"An error occurred while processing: {e}"

        return output

    def query_user_for_input(self):
        """ Continuously prompts the user for questions until they choose to exit. """
        while True:
            new_question = input("Please enter your question (or type 'exit' to quit): ")
            if Utility.is_exit_command(new_question):
                print("Exiting the question loop.")
                break
            elif Utility.is_valid_question(new_question):
                self.process_question(new_question)
            else:
                print("Invalid question. Please try again.")

    def process_question(self, question: str):
        """Process and store the user's question."""
        response = self.think([question])
        self.history.append((question, response))

    @staticmethod
    def get_relevant_files(input: List[str]) -> List[str]:
        """Retrieves relevant files based on the input question.

        :param: input (List[str]): A list of input questions.
        :return: List[str]: A list of selected file names that are deemed relevant.
        """
        evaluation_files = FileManagement.list_file_names()
        summariser = Summariser("in_thinker")
        summariser.summarise_files(evaluation_files)

        executor = BasePersona.create_ai_wrapper([])

        output = executor.execute_function(
            [ThinkerSpecification.build_file_query_prompt(evaluation_files)],
            input,
            SELECT_FILES_FUNCTION_SCHEMA
        )
        selected_files = output.get('files', [])

        logging.info(f"Selected: {selected_files}, \nfrom: {evaluation_files}")
        return selected_files

    def self_converse(self, initial_message: str):
        """
        Engage in a back-and-forth dialogue with another Thinker instance.
        """
        #ToDo should be selected from via AI call
        analyser_messages = [
            "Examine the current implementation and your answer for any logical inconsistencies or flaws. Identify specific areas where the logic might fail or where the implementation does not meet the requirements. Provide a revised version addressing these issues.",
            "Evaluate the current implementation for opportunities to enhance features, improve naming conventions, and increase documentation clarity. Assess readability and flexibility. Provide a revised version that incorporates these improvements.",
            "Review the structure and flow of the documentation in Thinker.py. Suggest and implement changes to improve the organization, clarity, and ease of understanding of the documentation. Provide a revised version with these changes.",
            "Present the final revised version of the code, incorporating all previous improvements we discussed. Additionally, provide a summary of the key changes made, explaining how each change enhances the code."
        ]

        prompt_messages = [initial_message] + analyser_messages
        for iteration, message in enumerate(prompt_messages):
            self.process_question(message)
            logging.info(f"Iteration {iteration} completed.")


if __name__ == '__main__':
    thinker = Thinker("proto")
    thinker.query_user_for_input()
    # thinker.self_converse("How would you improve the Thinker.py class")
