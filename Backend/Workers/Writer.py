from typing import Dict, Any

from Constants.WorkerSpecification import WriterSpecification
from Workers.BaseWorker import BaseWorker
from Workflows.AutoWorkflow import AutoWorkflow
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.WritePagesWorkflow import WritePagesWorkflow


class Writer(BaseWorker):
    """
    Writer worker, representing a role that manages writing tasks and their outputs

    This worker handles tasks such as creating new documents or appending to existing files.
    """

    # ToDo: Obviously later this should be updated later to just update the base workflows from BaseWorker
    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'chat': ChatWorkflow(),
        'write': WritePagesWorkflow(),
        'auto': AutoWorkflow(),
    }

    def __init__(self, name):
        super().__init__(name)
        self.instructions = WriterSpecification.WRITER_INSTRUCTIONS
        self.configuration = WriterSpecification.load_configuration()


if __name__ == '__main__':
    """Suggestions: 
    - Write a detailed report about the future of tidal technology, what innovations and possible disruptions could occur
    """
