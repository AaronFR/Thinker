import json
import logging
from typing import List, Tuple

from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import ThinkerSpecification
from Personas.PersonaSpecification.ThinkerSpecification import SELECT_FILES_FUNCTION_SCHEMA
from Personas.Summariser import Summariser
from Utilities.FileManagement import FileManagement
from Utilities.Utility import Utility


class Thinker:
    MAX_HISTORY = 5

    def __init__(self, name):
        super().__init__(name)
        self.history: List[Tuple[str, str]] = []  # To maintain question-response pairs

    def think(self, input: str) -> str:
        """Process the input question and think through a response."""
        logging.info("Thinking through the input: %s", input)
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
        """Continuously prompt the user for questions until they exit"""
        while True:
            new_question = input("Please enter your question (or type 'exit' to quit): ")
            if Utility.is_exit_command(new_question):
                print("Exiting the question loop.")
                break
            if Utility.is_valid_question(new_question):
                self.process_question(new_question)

    def process_question(self, question: str):
        """Process and store the user's question."""
        response = self.think([question])
        self.history.append((question, response))

    @staticmethod
    def get_relevant_files(input):
        evaluation_files = FileManagement.list_file_names()
        summariser = Summariser("in_thinker")
        summariser.summarise_files(evaluation_files)

        executor = BasePersona.create_ai_wrapper([])

        output = executor.execute_function(
            [ThinkerSpecification.build_file_query_prompt(evaluation_files)],
            [input],
            SELECT_FILES_FUNCTION_SCHEMA)
        selected_files = output.get('files', [])

        logging.info(f"Selected: {selected_files}, \nfrom: {evaluation_files}")
        return selected_files



if __name__ == '__main__':
    thinker = Thinker()
    thinker.query_user_for_input()
