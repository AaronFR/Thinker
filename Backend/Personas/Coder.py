import logging
from typing import List, Dict, Any
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import CoderSpecification
from Utilities.ErrorHandler import ErrorHandler
from Workflows.WorkflowManager import WorkflowManager
from Workflows.Workflows import WRITE_WORKFLOW, WRITE_TESTS_WORKFLOW, CHAT_WORKFLOW


class Coder(BasePersona):
    """
    Coding persona to write and edit code files.
    """

    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'write': WRITE_WORKFLOW,
        'write_tests': WRITE_TESTS_WORKFLOW,
        'chat': CHAT_WORKFLOW,
    }

    def __init__(self, name: str) -> None:
        """
        Initialize the Coder persona with a given name.

        :param name: The name of the coding persona.
        """
        super().__init__(name)
        self.workflow_manager = WorkflowManager()
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()
        ErrorHandler.setup_logging()


if __name__ == '__main__':
    """
    Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain,
    assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """

    coder = Coder("prototype")
    coder.query_user_for_input()
