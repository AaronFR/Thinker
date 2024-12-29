import logging
from typing import List, Dict, Any

from Utilities.ErrorHandler import ErrorHandler
from Personas.PersonaSpecification import WriterSpecification
from Personas.BasePersona import BasePersona
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.WritePagesWorkflow import WritePagesWorkflow


class Writer(BasePersona):
    """
    Writer persona, representing a role that manages writing tasks and their outputs

    This persona handles tasks such as creating new documents or appending to existing files.
    """

    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'write': WritePagesWorkflow(),
        'chat': ChatWorkflow(),
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

    writer = Writer("prototype")
    writer.query_user_for_input()
