from typing import Dict, Any
from Workers.BaseWorker import BaseWorker
from Constants.WorkerSpecification import CoderSpecification
from Workflows.AutoWorkflow import AutoWorkflow
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.WriteWorkflow import WriteWorkflow


class Coder(BaseWorker):
    """
    Coding worker to write and edit code files.
    """

    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'chat': ChatWorkflow(),
        'write': WriteWorkflow(),
        'auto': AutoWorkflow(),
    }

    def __init__(self, name: str) -> None:
        """
        Initialize the Coder worker with a given name.

        :param name: The name of the coding worker.
        """
        super().__init__(name)
        self.instructions = CoderSpecification.CODER_INSTRUCTIONS
        self.configuration = CoderSpecification.load_configuration()


if __name__ == '__main__':
    """
    Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain,
    assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """
