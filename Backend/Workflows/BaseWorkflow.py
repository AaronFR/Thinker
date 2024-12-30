
from abc import abstractmethod
from typing import Callable, Any, List

from flask_socketio import emit
from pathlib import Path

from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context

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
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
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

        BaseWorkflow.emit_step_completed_events(iteration, streaming, response)
        return response

    @staticmethod
    def _save_file_step(
        iteration: int,
        process_question: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        file_name: str,
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
        overwrite: bool = True
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
            selected_message_ids,
            model=model,
        )
        response = response + """
        
        """  # Otherwise when the next section is appended on it won't be on a new line


        user_id = get_user_context()
        file_path = Path(user_id).joinpath(file_name)

        StorageMethodology.select().save_file(response, str(file_path), overwrite=overwrite)

        BaseWorkflow.emit_step_completed_events(iteration, False, response)
        return response

    @staticmethod
    def emit_step_completed_events(iteration: int, streaming: bool, response: str):
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "streaming"})
        if not streaming:
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "response": response})
