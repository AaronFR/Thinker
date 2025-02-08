import logging
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask import copy_current_request_context
from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import ChatGptModel
from Constants.Exceptions import failure_to_process_individual_page_iteration
from Data.Files.StorageMethodology import StorageMethodology
from Functionality.Writing import Writing
from Utilities.Contexts import get_message_context, get_user_context, set_message_context, set_user_context
from Utilities.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Constants.Instructions import plan_pages_to_write, SIMPLE_SUMMARY_PROMPT
from Workflows.Workflows import generate_write_pages_workflow


class WritePagesWorkflow(BaseWorkflow):
    """
    Workflow for writing multiple pages based on user specifications.

    This workflow manages the creation of multiple pages by processing
    user instructions and generating corresponding files.
    """

    USE_PARALLEL_PROCESSING = True

    @return_for_error("An error occurred during the write pages workflow.", debug_logging=True)
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

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's guidance for writing pages.
        :param file_references: Optional list of file references.
        :param selected_message_ids: Optional list of selected message IDs for context.
        :param tags: Optional dictionary of additional metadata.
        :return: Summary of the AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        model = find_model_enum_value(tags.get("model") if tags else None)
        best_of = int(tags.get("best of", 1)) if tags else 1

        # Determine the number of pages to write
        page_count_str = tags.get("pages", "1") if tags else "1"
        try:
            page_count = int(page_count_str)
        except ValueError:
            logging.warning(f"Invalid page count '{page_count_str}'. Defaulting to 1.")
            page_count = 1

        if page_count > 10:
            logging.warning("Page count exceeds 10. Capping to 10 to prevent excessive resource usage.")
            page_count = 10

        # Generate and emit the workflow details
        workflow_details = generate_write_pages_workflow(
            initial_message=initial_message,
            page_count=page_count,
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        emit("send_workflow", {"workflow": workflow_details})

        iteration = 1
        pages = self._determine_pages_step(
            iteration=iteration,
            initial_message=initial_message,
            page_count=page_count,
            model=model
        )
        iteration += 1

        files = Writing.determine_files(initial_message, tags)
        file = files[0]  # Only one file generated at a time
        file_name = file['file_name']
        purpose = file['purpose']

        logging.info(f"Preparing to write to file: {file_name} with purpose: {purpose}")

        content = ""
        if self.USE_PARALLEL_PROCESSING:
            content = self.efficient_process_pages(
                pages,
                process_prompt,
                file_references,
                selected_message_ids,
                best_of,
                model,
                iteration
            )
            iteration = page_count + iteration
        else:
            for page_instruction in pages:
                content += self._chat_step(
                    iteration=iteration,
                    process_prompt=process_prompt,
                    message=page_instruction,
                    file_references=file_references or [],
                    selected_message_ids=selected_message_ids or [],
                    best_of=best_of,
                    streaming=False,
                    model=model,
                )
                iteration += 1

        file_path = Path(get_user_context()).joinpath(file_name)
        StorageMethodology.select().save_file(content, str(file_path), overwrite=False)

        summary = self._summary_step(
            iteration=iteration,
            process_prompt=process_prompt,
            message=SIMPLE_SUMMARY_PROMPT,
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            streaming=True,
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
        )

        return summary

    def efficient_process_pages(
        self,
        pages,
        process_prompt,
        file_references,
        selected_message_ids,
        best_of,
        model,
        iteration
    ):
        """
        Processes pages concurrently and efficiently concatenates the results.
        """
        message_id = get_message_context()
        user_id = get_user_context()

        num_pages = len(pages)
        results = [None] * num_pages  # Pre-allocate list for results

        with ThreadPoolExecutor(max_workers=min(32, num_pages)) as executor:  # Adjust max_workers as needed
            futures = []
            for i, page_instruction in enumerate(pages, 0):
                future = executor.submit(
                    copy_current_request_context(self.threaded_page_process),
                    page_instruction,
                    iteration + i,  # workflow steps are not 0-indexed
                    process_prompt,
                    file_references,
                    selected_message_ids,
                    best_of,
                    model,
                    message_id,
                    user_id
                )
                futures.append((i, future))  # Store index with the future

            for i, future in futures:
                try:
                    results[i] = future.result()  # Retrieve results in order
                except Exception:
                    logging.exception(failure_to_process_individual_page_iteration(i))
                    # Handle the error appropriately, e.g., log it, return an error string, etc.
                    results[i] = ""  # set to empty string if there's an error so other operations don't fail

        return ("\n\n".join(results)).strip()  # concatenate the results to one string.

    def threaded_page_process(self, page_instruction, iteration, process_prompt, file_references,
                              selected_message_ids, best_of, model, message_id, user_id):
        """Helper function to process a single page instruction."""
        set_message_context(message_id)
        set_user_context(user_id)

        response = self._chat_step(
            iteration=iteration,
            process_prompt=process_prompt,
            message=page_instruction,
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            best_of=best_of,
            streaming=False,
            model=model,
        )
        return response

    def _determine_pages_step(
        self,
        iteration: int,
        initial_message: str,
        page_count: int,
        model: ChatGptModel,
    ) -> List[str]:
        """
        Determine the list of page instructions to be processed.

        :param iteration: Current iteration number.
        :param initial_message: The user's guidance for writing pages.
        :param page_count: Number of pages to generate instructions for.
        :param model: The AI model to use.
        :return: List of page instruction messages.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

        response = AiOrchestrator().execute(
            [plan_pages_to_write(page_count)],
            [initial_message],
            model=model
        )

        pages = self.extract_markdown_list_items(response)
        if not pages:
            logging.error("No prompt suggestions were generated by the AI.")
            raise ValueError("No prompt suggestions were generated by the AI.")

        logging.info(f"Creating the following pages: {pages}")
        BaseWorkflow.emit_step_completed_events(iteration, streaming=False, response=response)
        return pages

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """
        Extract list items from markdown-formatted text, supporting both unordered and ordered lists.

        :param text: The text containing Markdown list items.
        :return: A list of extracted list items.
        """
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'
        matches = re.findall(pattern, text, re.MULTILINE)

        # Flatten matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        return extracted_items
