import logging
import re
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Workflows.Workflows import generate_auto_workflow


class AutoWorkflow(BaseWorkflow):
    """
    Workflow for automating a series of prompts, each file reference is fed as context into an individual prompt
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
        Execute all steps of the write pages workflow.

        :param process_prompt: Function to process user questions.
        :param initial_message: The user's guidance for writing code.
        :param file_references: References to relevant files.
        :param selected_message_ids: Selected message IDs for context.
        :param tags: Additional metadata.
        :return: AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        try:
            model = find_enum_value(tags.get("model")) if tags else None
            logging.info(f"☀ {file_references}")

            emit("send_workflow",
                 {"workflow": generate_auto_workflow(file_references,
                                                     selected_message_ids,
                                                     model.value)})

            iteration = 1
            for file_reference in file_references:
                file_name = file_reference.split("\\")[-1]
                logging.info(f"🌆 {file_reference} - {file_name}")
                self._save_file_step(
                    iteration=iteration,
                    process_prompt=process_prompt,
                    message=initial_message,
                    file_references=file_references,
                    selected_message_ids=selected_message_ids or [],
                    file_name=file_name,
                    model=model,
                    overwrite=False
                )
                iteration += 1

            summary = self._chat_step(
                iteration=iteration,
                process_prompt=process_prompt,
                message=f"Write a very quick summary to the effect that each file in {file_references} has been processed according to the initial user message: <user_message>{initial_message}</user_message>",
                file_references=[],
                selected_message_ids=[],
                streaming=True,
                model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
            )

            return summary
        except Exception as e:
            logging.exception("Failed to process write workflow")

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
            "Each prompt corresponds to one 'page'. Your prompts should be clear and concise, while making sure "
            "that the list of prompts all together give valid and concise instructions that should fully satisfy all "
            "aspects of my next prompt."
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
        BaseWorkflow.emit_step_completed_events(iteration, False, response)
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

