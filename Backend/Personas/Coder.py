from typing import Dict, Any
from Personas.BasePersona import BasePersona
from Constants.PersonaSpecification import CoderSpecification
from Utilities.LogsHandler import LogsHandler
from Workflows.AutoWorkflow import AutoWorkflow
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.LoopWorkflow import LoopWorkflow
from Workflows.WriteWorkflow import WriteWorkflow


class Coder(BasePersona):
    """
    Coding persona to write and edit code files.
    """

    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'chat': ChatWorkflow(),
        'write': WriteWorkflow(),
        'auto': AutoWorkflow(),
        'loop': LoopWorkflow(),
    }

    def __init__(self, name: str) -> None:
        """
        Initialize the Coder persona with a given name.

        :param name: The name of the coding persona.
        """
        super().__init__(name)
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()
        LogsHandler.setup_logging()


if __name__ == '__main__':
    """
    Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain,
    assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """
