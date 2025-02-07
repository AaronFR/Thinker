import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional, List, Dict

from flask import copy_current_request_context, g
from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import add_to_expensed_nodes, get_message_context, get_user_context, set_message_context, \
    set_user_context
from Utilities.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
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

        summary_message = (
            f"Write a very quick summary indicating that each file in {file_references} has been processed "
            f"according to the initial user message: <user_message>{initial_message}</user_message>"
        )
        summary = self._summary_step(
            iteration=len(file_references) + 1,
            process_prompt=process_prompt,
            message=summary_message,
            file_references=file_references,
            selected_message_ids=[],
            streaming=True,
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
        )

        return summary

    def _execute_parallel(
            self,
            process_prompt: Callable[[str, List[str], Dict[str, str]], str],
            initial_message: str,
            file_references: List[str],
            selected_message_ids: List[str],
            best_of: int,
            model: ChatGptModel,
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

        def wrapped_process_file(file_ref, iteration_id, message_id, user_id):
            """
            Note: it's at this exact point that the flask g context isn't passed and needs to be re-initialised for the
            thread
            """
            set_message_context(message_id)
            set_user_context(user_id)
            return self._process_file(process_prompt, initial_message, file_ref, selected_message_ids, best_of, model,
                                      iteration_id, message_id, user_id)

        with ThreadPoolExecutor(max_workers=len(file_references)) as executor:
            future_to_file = {
                executor.submit(copy_current_request_context(wrapped_process_file), file_ref, iteration_id + 1, message_id, user_id): file_ref
                for iteration_id, file_ref in enumerate(file_references)
            }

            for future in as_completed(future_to_file):
                file_ref = future_to_file[future]
                try:
                    iteration_id, response = future.result()
                    logging.info(f"Processed file '{file_ref}' successfully (Iteration {iteration_id}).")
                except Exception as e:
                    logging.exception(f"Error processing file '{file_ref}': {e}")

    def _execute_sequential(
            self,
            process_prompt: Callable[[str, List[str], Dict[str, str]], str],
            initial_message: str,
            file_references: List[str],
            selected_message_ids: List[str],
            best_of: int,
            model: ChatGptModel,
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

            prompt_message = f"{initial_message}\n\nSpecifically focus on {file_name}."
            response = self._save_file_step(
                iteration=iteration_id,
                process_prompt=process_prompt,
                message=prompt_message,
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
            model: ChatGptModel,
            iteration_id: int,
            message_id: str = None,
            user_id: str = None,
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
        prompt_message = f"{initial_message}\n\nSpecifically focus on {file_name} for iteration #{iteration_id}."
        response = self._save_file_step(
            iteration=iteration_id,
            process_prompt=process_prompt,
            message=prompt_message,
            file_references=[file_reference],
            selected_message_ids=selected_message_ids or [],
            file_name=file_name,
            best_of=best_of,
            model=model,
            overwrite=True,
            message_id=message_id,
            user_id=user_id
        )
        return iteration_id, response

    def _determine_pages_step(
        self,
        iteration: int,
        initial_message: str,
        page_count: int,
        model: ChatGptModel,
    ) -> List[str]:
        """
        Determine the list of files to be processed.

        ToDo: Look at how llm execution logic is run, process_prompt doesn't allow for custom system messages but
         AiOrchestrator calls aren't setup to process message or file reference ids

        :param initial_message: The user's guidance for writing code.
        :param page_count: User specified page count.
        :param model: The model to run
        :return: List of files with their purposes.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

        prompt = (
            "Just give a mark down list of prompts to be used to create a series of pages based on the following user "
            "prompt. "
            "Each prompt corresponds to one 'page'. Ensure that all prompts are clear, concise, and collectively "
            "provide valid and comprehensive instructions to fully satisfy the user's needs. "
            "If it would be beneficial to think through the problem please do so outside and before your list of "
            "prompts."
            f"I expect {page_count} prompts. No more no less."
        )
        response = AiOrchestrator().execute(
            [prompt],
            [initial_message],
            model=model
        )

        pages = self.extract_markdown_list_items(response)
        if not pages:
            raise Exception("No prompt suggestions generated!")

        logging.info(f"Creating the following pages: {pages}")
        BaseWorkflow.emit_step_completed_events(iteration, streaming=False, response=response)
        return pages

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """Extracts list items from markdown-formatted text, including both unordered and ordered lists.

        :param text: The text containing Markdown list items.
        :returns: A list of strings containing the extracted list items.
        """
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'

        matches = re.findall(pattern, text, re.MULTILINE)

        # Flatten the matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        return extracted_items
