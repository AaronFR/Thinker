import logging
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from Functionality.Coding import Coding
from Functionality.Writing import Writing

from Utilities.Contexts import get_user_context
from Utilities.Decorators.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Constants.Instructions import write_file, write_code_file, plan_file_creation, SIMPLE_SUMMARY_PROMPT
from Workflows.Workflows import generate_write_workflow


class WriteWorkflow(BaseWorkflow):
    """
    Workflow for writing code based on user specifications.

    This workflow manages the process of creating code files by interacting
    with the user through a series of prompts and saving the generated code
    appropriately.
    """

    @return_for_error("An error occurred during the write workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Execute all steps of the write workflow.

        :param process_prompt: Function to process user questions.
        :param initial_message: The user's guidance for writing code.
        :param file_references: References to relevant files.
        :param selected_message_ids: Selected message IDs for context.
        :param tags: Additional metadata.
        :return: AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        model = find_model_enum_value(tags.get("model") if tags else None)
        best_of = int(tags.get("best of", 1)) if tags else 1
        loops = int(tags.get("loops", 1)) if tags else 1

        emit("send_workflow",
             {"workflow": generate_write_workflow(initial_message, file_references, selected_message_ids,
                                                  model.value, best_of, loops,)})

        files = Writing.determine_files(initial_message, tags)
        for file in files:
            file_name = file['file_name']
            emit(UPDATE_WORKFLOW_STEP, {"step": 2, "file_name": file_name})
            user_id = get_user_context()
            file_path = Path(user_id).joinpath(file_name)
            purpose = file.get('purpose', "")

            logging.info(f"Writing code to {file_path}, \nPurpose: {purpose}")

            # ToDo: You should check if this pre-planning stage has value and to what degree if so
            self._chat_step(
                iteration=1,
                process_prompt=process_prompt,
                message=plan_file_creation(initial_message, file_name),
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                best_of=best_of,
                loops=loops,
                streaming=False,
                model=model,
            )

            self._save_file_step(
                iteration=2,
                process_prompt=process_prompt,
                message=write_code_file(file_name, purpose) if Coding.is_coding_file(file_name)
                else write_file(file_name, purpose),
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                file_name=file_name,
                model=model,
            )

        summary = self._summary_step(
            iteration=3,
            process_prompt=process_prompt,
            message=SIMPLE_SUMMARY_PROMPT,
            file_references=file_references,
            selected_message_ids=[],
            streaming=True,
        )

        return summary
