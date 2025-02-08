from typing import Dict, Any

from Utilities.ErrorHandler import ErrorHandler
from Constants.PersonaSpecification import WriterSpecification
from Personas.BasePersona import BasePersona
from Workflows.AutoWorkflow import AutoWorkflow
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.LoopWorkflow import LoopWorkflow
from Workflows.WritePagesWorkflow import WritePagesWorkflow


class Writer(BasePersona):
    """
    Writer persona, representing a role that manages writing tasks and their outputs

    This persona handles tasks such as creating new documents or appending to existing files.
    """

    # ToDo: Obviously later this should be updated later to just update the base workflows from BasePersona
    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'chat': ChatWorkflow(),
        'write': WritePagesWorkflow(),
        'auto': AutoWorkflow(),
        'loop': LoopWorkflow(),
    }

    def __init__(self, name):
        super().__init__(name)
        self.instructions = WriterSpecification.WRITER_INSTRUCTIONS
        self.configuration = WriterSpecification.load_configuration()

        ErrorHandler.setup_logging()


if __name__ == '__main__':
    """Suggestions: 
    - Write a detailed report about the future of tidal technology, what innovations and possible disruptions could occur
    """
