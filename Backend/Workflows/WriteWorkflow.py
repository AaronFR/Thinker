import logging
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Functionality.Coding import Coding
from Functionality.Writing import Writing

from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow
from Workflows.Instructions import write_file, write_code_file, plan_file_creation
from Workflows.Workflows import WRITE_WORKFLOW


class WriteWorkflow(BaseWorkflow):
    """
    Workflow for writing code based on user specifications.
    """

    @return_for_error("An error occurred during the write workflow.", debug_logging=True)
    def execute(
        self,
        process_question: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Execute all steps of the write workflow.

        :param process_question: Function to process user questions.
        :param initial_message: The user's guidance for writing code.
        :param file_references: References to relevant files.
        :param selected_message_ids: Selected message IDs for context.
        :param tags: Additional metadata.
        :return: AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        emit("send_workflow", {"workflow": WRITE_WORKFLOW})
        try:
            model = find_enum_value(tags.get("model")) if tags else None

            files = Writing.determine_files(initial_message, tags)
            summary = ""
            for file in files:
                file_name = file['file_name']
                user_id = get_user_context()
                file_path = Path(user_id).joinpath(file_name)
                purpose = file['purpose']

                logging.info(f"Writing code to {file_path}, \nPurpose: {purpose}")

                # ToDo: You should check if this pre-planning stage has value and to what degree if so
                self._chat_step(
                    iteration=1,
                    process_question=process_question,
                    message=plan_file_creation(initial_message, file_name),
                    file_references=file_references or [],
                    selected_message_ids=selected_message_ids or [],
                    streaming=False,
                    model=model,
                )

                self._save_file_step(
                    iteration=2,
                    process_question=process_question,
                    message=write_code_file(file_name, purpose) if Coding.is_coding_file(file_name)
                    else write_file(file_name, purpose),
                    file_references=[],
                    selected_message_ids=[],
                    file_name=file_name,
                    model=model,
                )

                summary = self._chat_step(
                    iteration=3,
                    process_question=process_question,
                    message="Very quickly summarize what you just wrote and where you wrote it.",
                    file_references=file_references or [],
                    selected_message_ids=selected_message_ids or [],
                    streaming=True,
                    model=ChatGptModel.CHAT_GPT_4_OMNI_MINI,
                )

            return summary
        except Exception as e:
            logging.exception("Failed to process write workflow")
