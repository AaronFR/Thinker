import logging
from typing import Dict, Any
import importlib

from flask_socketio import emit
from Utilities.ErrorHandler import ErrorHandler
from Workflows.BaseWorkflow import BaseWorkflow
from Workflows.ChatWorkflow import ChatWorkflow
from Workflows.WriteWorkflow import WriteWorkflow

UPDATE_WORKFLOW_STEP = "update_workflow_step"


class WorkflowManager:
    """
    Manages the execution of specific workflows for personas.

    :ivar workflows: A dictionary mapping workflow names to their corresponding workflow instances.
    """

    def __init__(self):
        """
        Initializes the WorkflowManager by loading specified workflows and setting up logging.
        """
        self.workflows: Dict[str, BaseWorkflow] = {
            "chat": ChatWorkflow(),
            "write": WriteWorkflow()
        }
        ErrorHandler.setup_logging()

    def execute_workflow(self, name: str, *args, **kwargs) -> Any:
        """
        Executes the specified workflow.

        :param name: Name of the workflow.
        :param args: Positional arguments for the workflow.
        :param kwargs: Keyword arguments for the workflow.
        :return: The result of the workflow execution.
        :raises ValueError: If the workflow does not exist.
        """
        if name not in self.workflows:
            logging.error(f"Workflow '{name}' not found.")
            raise ValueError(f"Workflow '{name}' not found.")

        logging.info(f"Executing workflow '{name}'.")
        emit("update_workflow", {"status": "in-progress"})

        result = self.workflows[name].execute(*args, **kwargs)

        emit("update_workflow", {"status": "finished"})
        return result
