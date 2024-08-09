import os
import re
from pprint import pformat
from typing import List

import Constants
import Globals
from ExecutionLogs import ExecutionLogs
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

    def execute_task(self, current_task: str):
        """First create a document evaluating the current output, if any, against the initial problem
        Then generate a list of workers to improve the current solution
        """
        self.files_for_evaluation = FileManagement.list_files(str(Globals.thought_id))

        # evaluate current files
        analyst = self.create_ai_wrapper(self.files_for_evaluation)
        analysis_report = analyst.execute(
            [PersonaConstants.ANALYST_SYSTEM_INSTRUCTIONS],
            [f"""For the following user request: {current_task} how do you evaluate the current available files as a solution?:
            Make as many notes and corrections as you possibly can"""]
        )

        # save to Analysis.txt file
        FileManagement.save_file(analysis_report, Constants.meta_analysis_filename, overwrite=True)
        ExecutionLogs.add_to_logs("Analyst: Report written and saved")

        # Search for the pattern
        is_solved = re.search(r"Solved:\s*True", analysis_report)

        # Check if the pattern was found and print it
        if is_solved:
            ExecutionLogs.add_to_logs("TASK SOLVED")
            Globals.solved = True

        # create json file assigning next workers
        Globals.workers = self.recommend_workers(current_task)
        ExecutionLogs.add_to_logs("Analyst suggested the following workers to work with the following instructions:\n"
                                  + pformat(Globals.workers, width=300))

    def recommend_workers(self, user_request) -> List[str]:
        analyst = self.create_ai_wrapper([Constants.meta_analysis_filename])
        function_output = analyst.execute_function(
            [PersonaConstants.ANALYST_FUNCTION_INSTRUCTIONS],
            [f"Initial user request: {user_request}"],
            PersonaConstants.ANALYST_FUNCTION_SCHEMA
        )

        workers = function_output.get('workers')
        return workers


if __name__ == '__main__':
    testAnalyst = Analyst("test")
    testAnalyst.execute_task("Write a report on the history of Netherlands in het Nederlands")
