import json
import logging
from typing import List

from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import ThinkerSpecification
from Personas.PersonaSpecification.ThinkerSpecification import SELECT_FILES_FUNCTION_SCHEMA
from Personas.Summariser import Summariser
from Utilities.FileManagement import FileManagement
from Utilities.Utility import Utility


class Thinker:
    MAX_HISTORY = 5

    def __init__(self):
        self.history = []

    def think(self, input: str) -> str:
        """Process the input question and think through a response."""
        logging.info("Thinking through the input: %s", input)
        try:
            selected_files = self.get_relevant_files(input)
            executor = BasePersona.create_ai_wrapper(selected_files)

            output = executor.execute(
                ["Just think through the question, step by step, ok?"],
                [input],
                assistant_messages=self.history
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
        response = self.think(question)
        self.append_to_history(response)

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

    def append_to_history(self, entry):
        """Append a new entry to the history, maintaining a size limit."""
        self.history.append(entry)
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)  # remove the oldest entry


if __name__ == '__main__':
    thinker = Thinker()
    thinker.query_user_for_input()
