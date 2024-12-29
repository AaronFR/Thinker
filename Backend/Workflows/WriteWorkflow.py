import logging
from pathlib import Path
from typing import Callable, Optional, List, Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Data.Configuration import Configuration
from Functionality.Coding import Coding
from Personas.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA
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

            files = self._determine_files(initial_message, tags)
            summary = ""
            for file in files:
                file_name = file['file_name']
                user_id = get_user_context()
                file_path = Path(user_id).joinpath(file_name)
                purpose = file['purpose']

                logging.info(f"Writing code to {file_path}, \nPurpose: {purpose}")

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
                    file_references=file_references or [],
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

    def _determine_files(
        self,
        initial_message: str,
        tags: Optional[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """
        Determine the list of files to be processed.

        :param initial_message: The user's guidance for writing code.
        :param tags: Additional metadata.
        :return: List of files with their purposes.
        """
        config = Configuration.load_config()

        if tags and tags.get("write"):
            files = [{
                "file_name": tags.get("write"),
                "purpose": "create from scratch"
            }]
        else:
            prompt = (
                "Give just a filename (with extension) that should be worked on given the following prompt. "
                "No commentary. "
                "If appropriate, write multiple files, the ones at the top of the class hierarchy first/on the top."
            ) if config['beta_features']['multi_file_processing_enabled'] else (
                "Give just a filename (with extension) that should be worked on given the following prompt. "
                "No commentary. Select only one singular file alone."
            )

            self.executor = AiOrchestrator()
            files = self.executor.execute_function(
                [prompt],
                [initial_message],
                GENERATE_FILE_NAMES_FUNCTION_SCHEMA
            )['files']

        logging.info(f"Referencing/Creating the following files: {files}")
        return files
