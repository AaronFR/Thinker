
from abc import abstractmethod
from typing import Callable, Any, List

from flask_socketio import emit
from pathlib import Path

from AiOrchestration.ChatGptModel import ChatGptModel
from Utilities.Contexts import get_user_context
from Functionality.Coding import Coding
from Personas.PersonaSpecification import PersonaConstants

UPDATE_WORKFLOW_STEP = "update_workflow_step"


class BaseWorkflow:
    """
    Abstract base class for all workflows.
    """

    @abstractmethod
    def execute(self, process_question: Callable, **kwargs) -> Any:
        """
        Executes the workflow with the given parameters.

        :param process_question: Function to process user questions.
        :param kwargs: Additional arguments specific to the workflow.
        :return: Result of the workflow execution.
        """
        pass

    @staticmethod
    def _chat_step(
        iteration: int,
        process_question: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        streaming: bool = True,
        model: str = ChatGptModel.CHAT_GPT_4_OMNI_MINI.value,
    ) -> str:
        """
        Handles individual chat steps.

        :param iteration: Current iteration number.
        :param process_question: Function to process user questions.
        :param message: The message to process.
        :param file_references: References to files.
        :param selected_message_ids: Selected message IDs for context.
        :param streaming: Whether to stream the response.
        :param model: The AI model to use.
        :return: AI's response.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        response = process_question(
            message,
            file_references,
            selected_message_ids,
            streaming=streaming,
            model=model,
        )
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})
        return response

    @staticmethod
    def _save_file_step(
        iteration: int,
        process_question: Callable,
        message: str,
        file_references: List[str],
        file_name: str,
        model: str = ChatGptModel.CHAT_GPT_4_OMNI_MINI.value,
    ) -> str:
        """
        Handles the process of saving files.

        :param iteration: Current iteration number.
        :param process_question: Function to process user questions.
        :param message: The message to process.
        :param file_references: References to files.
        :param file_name: Name of the file to save.
        :param model: The AI model to use.
        :return: AI's response.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        response = process_question(
            message,
            file_references,
            model=model,
        )

        user_id = get_user_context()
        file_path = Path(user_id).joinpath(file_name)

        Coding.write_to_file_task({
            PersonaConstants.SAVE_TO: file_path,
            PersonaConstants.INSTRUCTION: response
        })

        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})
        return response
