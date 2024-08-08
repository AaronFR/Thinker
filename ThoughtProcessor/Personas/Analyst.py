import os
from pprint import pformat
from typing import List

import Constants
import Globals
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.FileManagement import FileManagement
from ThoughtProcessor.Personas import PersonaConstants
from ThoughtProcessor.Personas.BasePersona import BasePersona


class Analyst(BasePersona):

    def __init__(self, name):
        super().__init__(name)
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")
        self.files_for_evaluation = []
        Globals.thought_id = 1  # self.get_next_thought_id()

        ErrorHandler.setup_logging()

    def work(self, current_task: str):
        """First create a document evaluating the current output, if any, against the initial problem
        Then generate a list of workers to improve the current solution
        """
        execution_logs = f"Analyst analysing...:\n{current_task}\n"
        self.files_for_evaluation = FileManagement.list_files(str(Globals.thought_id))

        # evaluate current files
        analyst = self.create_ai_wrapper(self.files_for_evaluation)
        analysis_report = analyst.execute(
            ["""You are an analyst strictly reviewing the quality of a solution to a given problem, at the end of your through evaluation, determine if the given solution ACTUALLY answers the original prompt sufficiently in format:
                    Solved: True/False. Also make it clear that this is just a report and should not be operated on by other worker LLM's"""],
            [f"given the following user request: {current_task} how do you evaluate the current available files as a solution?:\n\n\n Make as many notes and corrections as you possibly can"]
        )

        # save to Analysis.txt file
        FileManagement.save_file(analysis_report, Constants.meta_analysis_filename, overwrite=True)
        execution_logs += "Analyst: Report written and saved"

        # create json file assigning next workers
        Globals.workers = self.recommend_workers(current_task)
        execution_logs += "Analyst suggested the following workers to work with the following instructions:\n" + pformat(Globals.workers)

        FileManagement.save_file(execution_logs, Constants.execution_logs_filename)

    def recommend_workers(self, user_request) -> List[str]:
        analyst = self.create_ai_wrapper([Constants.meta_analysis_filename])
        dict = analyst.execute_function(
            [PersonaConstants.ANALYST_FUNCTION_INSTRUCTIONS],
            [f"Initial user request: {user_request}"],
            PersonaConstants.ANALYST_FUNCTION_SCHEMA
        )

        print(dict)
        list = dict.get('workers')
        print(list)

        return list


if __name__ == '__main__':
    testAnalyst = Analyst("test")
    testAnalyst.work("Write a report on the history of Netherlands in het Nederlands")
