import logging
from typing import List
from Personas.BasePersona import BasePersona
from Personas.PersonaSpecification import CoderSpecification
from Utilities.ErrorHandler import ErrorHandler
from Workflows.WorkflowManager import WorkflowManager


class Coder(BasePersona):
    """
    Coding persona to write and edit code files.
    """

    def __init__(self, name):
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
                     tags: List[str] = None):
        """
        Determines and executes the appropriate workflow based on user input and tags.

        :param initial_message: The user's initial message or prompt.
        :param file_references: List of file paths referenced in the workflow.
        :param selected_message_ids: UUIDs of previously selected messages for context.
        :param tags: Additional tags to influence workflow selection.
        :return: The last response message from the executed workflow.
        """
        tags = tags or {}

        if tags.get("write"):
            return self.workflow_manager.execute_workflow(
                "write",
                self.process_question,
                initial_message,
                file_references,
                selected_message_ids,
                tags
            )
        if tags.get("write_tests"):
            return self.workflow_manager.execute_workflow(
                "write_tests",
                self.process_question,
                initial_message,
                file_references,
                selected_message_ids,
                tags
            )

        return self.workflow_manager.execute_workflow(
            "chat",
            self.process_question,
            initial_message,
            file_references,
            selected_message_ids,
            tags
        )


if __name__ == '__main__':
    """Suggestions:
    - generate a method for calculating the 'ruggedness' of a area of terrain, 
     assume the terrain is entered as a 2d data plot
    - How would you improve the Thinker.py class?
    """

    coder = Coder("prototype")
    coder.query_user_for_input()
