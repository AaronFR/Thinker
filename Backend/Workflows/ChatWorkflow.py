import logging
from typing import Callable, Optional, List, Dict

from AiOrchestration.ChatGptModel import find_enum_value
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow


class ChatWorkflow(BaseWorkflow):
    """
    Handles chat-based interactions with the user.
    """

    @return_for_error("An error occurred during the chat workflow.", debug_logging=True)
    def execute(
        self,
        process_question: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes the chat workflow.

        :param process_question: Function to process user questions.
        :param initial_message: The user's initial prompt.
        :param file_references: References to relevant files.
        :param selected_message_ids: IDs of selected messages for context.
        :param tags: Additional metadata.
        :return: AI's response.
        """
        logging.info("Chat workflow selected")
        model = find_enum_value(tags.get("model"))

        response = self._chat_step(
            iteration=1,
            process_question=process_question,
            message=initial_message,
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            streaming=True,
            model=model,
        )

        return response
