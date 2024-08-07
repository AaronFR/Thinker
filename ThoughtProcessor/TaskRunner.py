import os
from ThoughtProcessor.ErrorHandler import ErrorHandler
from ThoughtProcessor.Personas.Analyst import Analyst
from ThoughtProcessor.Personas.Writer import Writer

class TaskRunner:
    def __init__(self, current_thought_id: int):
        self.current_thought_id = current_thought_id
        self.thoughts_folder = os.path.join(os.path.dirname(__file__), "thoughts")

        self.personas = {
            'analyst': Analyst('analyst'),
            # 'researcher': Researcher('researcher'),
            'writer': Writer('writer')
            # 'editor': Editor('editor')
        }

        ErrorHandler.setup_logging()

    def run_iteration(self, current_task: str, persona='writer'):
        """
        Orchestrate the execution of tasks based on the current user prompt.
        ToDo: implement system for dealing with failed tasks

        :param current_task: the initial user prompt
        :param persona: the assigned 'role' to operate in at the given stage of the application
        """
        self.personas.get(persona).work(current_task)
