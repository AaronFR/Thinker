import logging
import re
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Functionality.Writing import Writing
from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow
from Workflows.Instructions import write_file, write_code_file, plan_file_creation
from Workflows.Workflows import WRITE_PAGES_WORKFLOW


class WritePagesWorkflow(BaseWorkflow):
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
        Execute all steps of the write pages workflow.

        :param process_question: Function to process user questions.
        :param initial_message: The user's guidance for writing code.
        :param file_references: References to relevant files.
        :param selected_message_ids: Selected message IDs for context.
        :param tags: Additional metadata.
        :return: AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        emit("send_workflow", {"workflow": WRITE_PAGES_WORKFLOW})
        try:
            model = find_enum_value(tags.get("model")) if tags else None

            pages = self._determine_pages(initial_message, tags)

            files = Writing.determine_files(initial_message, tags)
            file = files[0]  # only one file generated at a time
            file_name = files[0]['file_name']
            purpose = file['purpose']


            for page_instruction in pages:

                self._save_file_step(
                    iteration=1,
                    process_question=process_question,
                    message=page_instruction,
                    file_references=file_references or [],
                    selected_message_ids=selected_message_ids or [],
                    file_name=file_name,
                    model=model,
                    overwrite=False
                )

            summary = self._chat_step(
                iteration=3,
                process_question=process_question,
                message="Very quickly summarize all of what you just wrote and where you wrote it.",
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                streaming=True,
                model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
            )
            user_id = get_user_context()
            file_path = Path(user_id).joinpath(file_name)

            logging.info(f"Writing code to {file_path}, \nPurpose: {purpose}")

            return summary
        except Exception as e:
            logging.exception("Failed to process write workflow")

    def _determine_pages(
        self,
        initial_message: str,
        tags: Optional[Dict[str, str]],
    ) -> List[str]:
        """
        Determine the list of files to be processed.

        :param initial_message: The user's guidance for writing code.
        :param tags: Additional metadata.
        :return: List of files with their purposes.
        """
        pages = int(tags.get("pages", 1))
        if pages > 10:  # maxed at 10 to prevent expensive misinput till confirmation checks is added
            pages = 10

        prompt = (
            "Just give a mark down list of prompts to be used to create a series of pages based on the following user "
            "prompt. Each prompt corresponds to one 'page'. Your prompts should be clear and concise, while making sure "
            "that the list of prompts all together give valid and concise instructions that should fully satisfy all "
            "aspects of my next prompt."
            "If it would be beneficial to think through the problem please do so outside and before your list of "
            "prompts."
            f"I expect {pages} prompts. No more no less."
        )

        model = find_enum_value(tags.get("model")) if tags else None
        self.executor = AiOrchestrator()
        response = self.executor.execute(
            [prompt],
            [initial_message],
            model=model
        )

        pages = self.extract_markdown_list_items(response)
        if not pages:
            raise Exception("No prompt suggestions generated!")

        logging.info(f"Creating the following pages: {pages}")
        return pages

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """Extracts list items from markdown-formatted text, including both unordered and ordered lists.

        :param text: The text containing markdown list items.
        :returns: A list of strings containing the extracted list items.
        """
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'

        matches = re.findall(pattern, text, re.MULTILINE)

        # Flatten the matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        return extracted_items

