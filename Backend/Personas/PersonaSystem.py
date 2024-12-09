import os

from Personas.PersonaSpecification.PersonaConstants import ANALYST, WRITER, EDITOR
from Personas.Analyst import Analyst
from Personas.Editor import Editor
from Personas.Writer import Writer

from Utilities.ExecutionLogs import ExecutionLogs
from Utilities.ErrorHandler import ErrorHandler


class PersonaSystem:
    def __init__(self):
        self.file_data_directory = os.path.join(os.path.dirname(__file__), '..', 'Data', 'FileData')

        self.personas = {
            ANALYST: Analyst(ANALYST),
            # 'researcher': Researcher('researcher'),
            WRITER: Writer(WRITER),
            EDITOR: Editor(EDITOR)
        }

        ErrorHandler.setup_logging()

    def run_iteration(self, task_to_execute: str, persona=ANALYST):
        """Orchestrate the execution of tasks based on the current user prompt.
        ToDo: implement system for dealing with failed tasks

        :param task_to_execute: the initial user prompt
        :param persona: the assigned 'role' to operate in at the given stage of the application
        """
        ExecutionLogs.add_to_logs(f"{persona} assigned task: {task_to_execute}")
        self.personas[persona.lower()].execute_task(task_to_execute)
