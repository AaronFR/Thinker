import json
import logging

from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification.ThinkerSpecification import SELECT_FILES_FUNCTION_SCHEMA
from Personas.Summariser import Summariser
from Utilities.FileManagement import FileManagement


class Thinker:

    def __init__(self):
        self.history = []

    def think(self, input: str) -> str:
        executor = BasePersona.create_ai_wrapper(selected_files)
        output = executor.execute(
            ["Just think through the question, step by step, ok?"],
            [input],
            assistant_messages=self.history
        )
            selected_files = self.get_relevant_files(input)

        return output

    def query_user_for_input(self):
        while True:
            new_question = input("Please enter your question (or type 'exit' to quit): ")
            if new_question.lower() == 'exit':
                print("Exiting the question loop.")
                break
            self.history.append(self.think(new_question))

    @staticmethod
    def get_relevant_files(input):
        evaluation_files = FileManagement.list_file_names()
        summariser = Summariser("in_thinker")
        summariser.summarise_files(evaluation_files)
        executor = BasePersona.create_ai_wrapper([])

        output = executor.execute_function(
            [f"""From the list of files, choose which files are expressively explicitly relevant to my prompt. This could be one, many or NO
            files. By default DO NOT SELECT A FILE UNLESS EXPLICITLY RELATED TO THE INQUIRY
            files: {evaluation_files}: A file concerned with implementing a Thinker class in python, to implement AI calls """],
            [input],
            SELECT_FILES_FUNCTION_SCHEMA)
        selected_files = output['files']
        logging.info(f"Selected: {selected_files}, \nfrom: {evaluation_files}")
        return selected_files


if __name__ == '__main__':
    thinker = Thinker()
    thinker.query_user_for_input()