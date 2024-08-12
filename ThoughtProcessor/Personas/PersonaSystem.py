import os

from ThoughtProcessor.ExecutionLogs import ExecutionLogs
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.Personas import PersonaConstants
from ThoughtProcessor.Personas.Analyst import Analyst
from ThoughtProcessor.Personas.Editor import Editor
from ThoughtProcessor.Personas.Writer import Writer


class PersonaSystem:
    def __init__(self):
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "../thoughts")

        self.personas = {
            PersonaConstants.ANALYST: Analyst(PersonaConstants.ANALYST),
            # 'researcher': Researcher('researcher'),
            PersonaConstants.WRITER: Writer(PersonaConstants.WRITER),
            PersonaConstants.EDITOR: Editor(PersonaConstants.EDITOR)
        }

        ErrorHandler.setup_logging()

    def run_iteration(self, current_task: str, persona=PersonaConstants.ANALYST):
        """
        Orchestrate the execution of tasks based on the current user prompt.
        ToDo: implement system for dealing with failed tasks

        :param current_task: the initial user prompt
        :param persona: the assigned 'role' to operate in at the given stage of the application
        """
        ExecutionLogs.add_to_logs(f"{persona} assigned task: {current_task}")
        self.personas.get(persona.lower()).execute_task(current_task)
