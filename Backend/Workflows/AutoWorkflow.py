import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional, List, Dict

from flask import copy_current_request_context
from flask_socketio import emit

from AiOrchestration.AiModel import AiModel
from Constants.Exceptions import failure_to_process_file_in_workflow
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_message_context, get_user_context, set_message_context, set_user_context, \
    set_iteration_context, set_category_context, get_category_context
from Utilities.Decorators.Decorators import return_for_error
from Constants.Instructions import multiple_pages_summary_message, for_each_focus_on_prompt
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow
from Workflows.Workflows import generate_auto_workflow


class AutoWorkflow(BaseWorkflow):
    """
    Workflow for automating a series of prompts, where each file reference is used as context for individual prompts.

    Note:
        Saving files may take some time.
    """

    USE_PARALLEL_PROCESSING = True

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
        Execute all steps of the write pages workflow.
        ToDo: add settings to not incorporate history from one prompt to another

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's prompy.
        :param file_references: Optional list of file references.
        :param selected_message_ids: Optional list of selected message IDs for context.
        :param tags: Optional dictionary of additional metadata.
        :return: AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        model = find_model_enum_value(tags.get("model", None) if tags else None)
        best_of = int(tags.get("best of", 1)) if tags else 1  # type validation check needed

        if not file_references:
            logging.warning("No file references provided. Exiting AutoWorkflow.")
            return "No files to process."

        workflow_data = generate_auto_workflow(
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        emit("send_workflow", {"workflow": workflow_data})

        if not file_references:
            logging.warning("No file references provided. Exiting AutoWorkflow.")
            return "No files to process."

        if self.USE_PARALLEL_PROCESSING:
            self._execute_parallel(
                process_prompt, initial_message, file_references, selected_message_ids, best_of, model
            )
        else:
            self._execute_sequential(
                process_prompt, initial_message, file_references, selected_message_ids, best_of, model
            )

        summary = self._summary_step(
            iteration=len(file_references) + 1,
            process_prompt=process_prompt,
            message=multiple_pages_summary_message(file_references, initial_message),
            file_references=file_references,
            selected_message_ids=[],
            streaming=True,
        )

        return summary

    def _execute_parallel(
            self,
            process_prompt: Callable[[str, List[str], Dict[str, str]], str],
            initial_message: str,
            file_references: List[str],
            selected_message_ids: List[str],
            best_of: int,
            model: AiModel,
    ):
        """
        Executes the workflow steps in parallel.

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's prompt.
        :param file_references: List of file references.
        :param selected_message_ids: List of selected message IDs for context.
        :param best_of: Number indicating how many completions to generate server-side.
        :param model: The model to use for AI interactions.
        :return: Aggregated summary of all processing results.
        """
        message_id = get_message_context()
        user_id = get_user_context()
        category_id = get_category_context()

        def wrapped_process_file(file_ref, iteration_id, message_id, user_id, category_id):
            """
            Note: it's at this exact point that the flask g context isn't passed and needs to be re-initialised for the
            thread

            ToDo: Create a utility method shell for creating threads based on a function call
            """
            set_message_context(message_id)
            set_user_context(user_id)
            set_iteration_context(iteration_id)
            set_category_context(category_id)

            return self._process_file(
                process_prompt,
                initial_message,
                file_ref,
                selected_message_ids,
                best_of,
                model,
                iteration_id
            )

        with ThreadPoolExecutor(max_workers=len(file_references)) as executor:
            future_to_file = {
                executor.submit(
                    copy_current_request_context(wrapped_process_file),
                    file_ref,
                    iteration_id + 1,
                    message_id,
                    user_id,
                    category_id,
                ): file_ref
                for iteration_id, file_ref in enumerate(file_references)
            }

            for future in as_completed(future_to_file):
                file_ref = future_to_file[future]
                try:
                    iteration_id, response = future.result()
                    logging.info(f"Processed file '{file_ref}' successfully (Iteration {iteration_id}).")
                except Exception:
                    logging.exception(failure_to_process_file_in_workflow)

    def _execute_sequential(
            self,
            process_prompt: Callable[[str, List[str], Dict[str, str]], str],
            initial_message: str,
            file_references: List[str],
            selected_message_ids: List[str],
            best_of: int,
            model: AiModel,
    ):
        """
        Executes the workflow steps sequentially.

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's prompt.
        :param file_references: List of file references.
        :param selected_message_ids: List of selected message IDs for context.
        :param best_of: Number indicating how many completions to generate server-side.
        :param model: The model to use for AI interactions.
        :return: Aggregated summary of all processing results.
        """
        results = []
        for iteration_id, file_reference in enumerate(file_references, start=1):
            file_name = StorageMethodology().extract_file_name(file_reference)
            logging.info(
                f"Processing file '{file_reference}' (Extracted name: '{file_name}') - Iteration {iteration_id}.")

            response = self._save_file_step(
                iteration=iteration_id,
                process_prompt=process_prompt,
                message=for_each_focus_on_prompt(initial_message, file_name),
                file_references=[file_reference],
                selected_message_ids=selected_message_ids or [],
                file_name=file_name,
                best_of=best_of,
                model=model,
                overwrite=True
            )
            results.append(f"Iteration {iteration_id} for '{file_reference}': {response}")
            logging.debug(f"Response for iteration {iteration_id} on '{file_reference}': {response}")

    def _process_file(
            self,
            process_prompt: Callable[[str, List[str], Dict[str, str]], str],
            initial_message: str,
            file_reference: str,
            selected_message_ids: List[str],
            best_of: int,
            model: AiModel,
            iteration_id: int
    ) -> (int, str):
        """
        Helper method to process a single file in the workflow with a unique iteration ID.

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's prompt.
        :param file_reference: The file reference to process.
        :param selected_message_ids: List of selected message IDs for context.
        :param best_of: Number indicating how many completions to generate server-side.
        :param model: The model to use for AI interactions.
        :param iteration_id: Unique iteration ID for the processing step.
        :return: A tuple of iteration_id and the AI's response.
        """
        file_name = StorageMethodology().extract_file_name(file_reference)
        response = self._save_file_step(
            iteration=iteration_id,
            process_prompt=process_prompt,
            message=for_each_focus_on_prompt(initial_message, file_name, iteration_id),
            file_references=[file_reference],
            selected_message_ids=selected_message_ids or [],
            file_name=file_name,
            best_of=best_of,
            model=model,
            overwrite=True
        )
        return iteration_id, response
