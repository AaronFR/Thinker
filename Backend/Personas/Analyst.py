import os
import re

from pprint import pformat
from typing import List

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Files.StorageMethodology import StorageMethodology
from Personas.PersonaSpecification import PersonaConstants, AnalystSpecification
from Personas.BasePersona import BasePersona
from Utilities import Globals
from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.ErrorHandler import ErrorHandler


class Analyst(BasePersona):

    def __init__(self, name):
        super().__init__(name)
        self.file_data_directory = os.path.join(os.path.dirname(__file__), "thoughts")
        self.evaluation_files = []

        ErrorHandler.setup_logging()

    def execute_task(self, task_to_execute: str):
        """First create a document evaluating the current output, if any, against the initial problem
        Then generate a list of workers to improve the current solution

        ToDo: In the new system this will probably be saved as a node, if used
        """
        self.evaluation_files = StorageMethodology.select().list_staged_files()

        # evaluate current files
        analyst = AiOrchestrator(self.evaluation_files)
        analysis_report = analyst.execute(
            [AnalystSpecification.ANALYST_SYSTEM_INSTRUCTIONS],
            [f"For the following user request: {task_to_execute} how do you evaluate the current available files as a"
             " solution?: Make as many notes and corrections as you possibly can"]
        )

        # save to Analysis.txt file_name
        file_path = "CATEGORY_ID_PLACEHOLDER\\" + PersonaConstants.meta_analysis_filename
        StorageMethodology.select().save_file(analysis_report, file_path, overwrite=True)
        ExecutionLogs.add_to_logs("Analyst: Report written and saved")

        # Search for the pattern
        is_solved = re.search(r"Solved:\s*True", analysis_report)

        # Check if the pattern was found and print it
        if is_solved:
            ExecutionLogs.add_to_logs("TASK SOLVED")
            Globals.is_solved = True

        # create json file_name assigning next workers
        Globals.workers = self.recommend_workers(task_to_execute)
        ExecutionLogs.add_to_logs("Analyst suggested the following workers to work with the following instructions:\n"
                                  + pformat(Globals.workers, width=300))

    @staticmethod
    def recommend_workers(user_request) -> List[str]:
        analyst = AiOrchestrator([PersonaConstants.meta_analysis_filename])
        function_output = analyst.execute_function(
            [AnalystSpecification.ANALYST_FUNCTION_INSTRUCTIONS],
            [f"Initial user request: {user_request}"],
            AnalystSpecification.ANALYST_FUNCTION_SCHEMA
        )

        return function_output[PersonaConstants.WORKERS]


if __name__ == '__main__':
    testAnalyst = Analyst("test")
    testAnalyst.execute_task("Write a report on the history of Netherlands in het Nederlands")
