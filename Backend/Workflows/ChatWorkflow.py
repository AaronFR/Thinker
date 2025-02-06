import logging
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from Utilities.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow
from Workflows.Workflows import generate_chat_workflow


class ChatWorkflow(BaseWorkflow):
    """
    Handles chat-based interactions with the user.

    This workflow manages the process of responding to user prompts
    and processing any relevant file references or selected messages.
    """

    @return_for_error("An error occurred during the chat workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes the chat workflow.

        ToDo: has a bad habit of saying 'the user' (this happens on Gemini too, its the system message)

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's initial prompt.
        :param file_references: Optional list of file references.
        :param selected_message_ids: Optional list of selected message IDs for context.
        :param tags: Optional dictionary of additional metadata.
        :return: AI's response.
        """
        logging.info("Chat workflow selected")

        # ToDo: Need to add a user configured default model instead of None
        model = find_model_enum_value(tags.get("model") if tags else None)
        best_of = int(tags.get("best of", 1)) if tags else 1  # type validation check needed
        workflow_details = generate_chat_workflow(
            initial_message=initial_message,
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        emit("send_workflow", {"workflow": workflow_details})

        response = self._chat_step(
            iteration=1,
            process_prompt=process_prompt,
            message=initial_message,
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            best_of=best_of,
            streaming=True,
            model=model,
        )

        return response
