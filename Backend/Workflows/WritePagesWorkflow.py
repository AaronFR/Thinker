import logging
import re
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import ChatGptModel
from Functionality.Writing import Writing
from Utilities.Contexts import add_to_expensed_nodes, get_message_context
from Utilities.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Workflows.Instructions import plan_pages_to_write
from Workflows.Workflows import generate_write_pages_workflow


class WritePagesWorkflow(BaseWorkflow):
    """
    Workflow for writing multiple pages based on user specifications.

    This workflow manages the creation of multiple pages by processing
    user instructions and generating corresponding files.
    """

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

        # Process each page instruction
        for page_instruction in pages:
            self._save_file_step(
                iteration=iteration,
                process_prompt=process_prompt,
                message=page_instruction,
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                best_of=best_of,
                file_name=file_name,
                model=model,
                overwrite=True
            )
            iteration += 1

        summary = self._summary_step(
            iteration=iteration,
            process_prompt=process_prompt,
            message="Very quickly summarise what you just wrote and where you wrote it.",
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            streaming=True,
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
        )

        return summary

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
        add_to_expensed_nodes(get_message_context())

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
