import logging
from typing import List, Dict, Callable, Any
from flask_socketio import emit
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

    def run_workflow(self,
                     initial_message: str,
                     file_references: List[str] = None,
                     selected_message_ids: List[str] = None,
                     tags: List[str] = None) -> Any:
        """
        Determines and executes the appropriate workflow based on user input and tags.

        :param initial_message: The user's initial message or prompt.
        :param file_references: List of file paths referenced in the workflow.
        :param selected_message_ids: UUIDs of previously selected messages for context.
        :param tags: Additional tags to influence workflow selection.
        :return: The last response message from the executed workflow.
        """
        tags = tags or {}
        workflow_key = self._determine_workflow_key(tags)

        if workflow_key:
            emit("send_workflow", {"workflow": self.WORKFLOWS[workflow_key]})
            return self.workflow_manager.execute_workflow(
                workflow_key,
                self.process_question,
                initial_message,
                file_references,
                selected_message_ids,
                tags
            )

        # Handle case where no valid workflow key is found
        emit("send_workflow", {"workflow": CHAT_WORKFLOW})
        return self.workflow_manager.execute_workflow(
            "chat",
            self.process_question,
            initial_message,
            file_references,
            selected_message_ids,
            tags
        )

    def _determine_workflow_key(self, tags: Dict[str, bool]) -> str:
        """
        Determines the workflow key based on tags.

        :param tags: A dictionary of tags provided by the user.
        :return: The key of the selected workflow or None if not found.
        """
        for key in self.WORKFLOWS.keys():
            if tags.get(key):
                return key
        return None


if __name__ == '__main__':
    """
    Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain,
    assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """

    coder = Coder("prototype")
    coder.query_user_for_input()
