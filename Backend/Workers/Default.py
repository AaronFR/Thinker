from typing import Dict, Any
from Workers.BaseWorker import BaseWorker
from Constants.WorkerSpecification import DefaultSpecification
from Workflows.AutoWorkflow import AutoWorkflow
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.WriteWorkflow import WriteWorkflow


class Default(BaseWorker):
    """
    Default worker, mostly to serve as a baseline while also tutorial-ising "well what's not default then?"
    """

    WORKFLOWS: Dict[str, Dict[str, Any]] = {
        'chat': ChatWorkflow(),
        'write': WriteWorkflow(),
        'auto': AutoWorkflow(),
    }

    def __init__(self, name: str) -> None:
        """
        Initialize the Default worker.

        :param name: The name of the coding worker.
        """
        super().__init__(name)
        self.instructions = DefaultSpecification.DEFAULT_INSTRUCTIONS
        self.configuration = DefaultSpecification.load_configuration()


if __name__ == '__main__':
    """
    Suggestions:
    - News
    - General Knowledge
    """
