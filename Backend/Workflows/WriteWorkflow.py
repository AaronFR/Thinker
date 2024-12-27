import logging
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask_socketio import emit
from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value
from Data.Configuration import Configuration
from Functionality.Coding import Coding
from Personas.PersonaSpecification.CoderSpecification import GENERATE_FILE_NAMES_FUNCTION_SCHEMA
from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP


class WriteWorkflow(BaseWorkflow):
    """
    Writes code based on the user's specifications.
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
        Executes the write workflow.

        :param process_question: Function to process user questions.
        :param initial_message: The user's guidance for writing code.
        :param file_references: References to relevant files.
        :param selected_message_ids: Selected message IDs for context.
        :param tags: Additional metadata.
        :return: AI's response.
        """
        executor = AiOrchestrator()
        config = Configuration.load_config()
        model = find_enum_value(tags.get("model"))

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

            files = executor.execute_function(
                [prompt],
                [initial_message],
                GENERATE_FILE_NAMES_FUNCTION_SCHEMA
            )['files']

        logging.info(f"Referencing/Creating the following files: {files}")

        for file in files:
            file_name = file['file_name']
            user_id = get_user_context()
            file_path = Path(user_id).joinpath(file_name)
            purpose = file['purpose']

            logging.info(f"Writing code to {file_path}, \nPurpose: {purpose}")

            if Coding.is_coding_file(file_name):
                step_two = (
                    f"Write/Rewrite {file_name} based on your previous plan of action and the actual contents of "
                    f"this particular file, focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
                    "Making sure that the file imports as necessary, referencing the appropriate classes. "
                    "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
                    "Unless explicitly requested, the file's content must be preserved by default."
                )
            else:
                step_two = (
                    f"Write/Rewrite {file_name} based on your previous plan of action for this particular file, "
                    f"focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
                    "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
                    "Unless explicitly requested, the file's content must be preserved by default."
                )

            analyser_messages = [
                f"<user_prompt>{initial_message}</user_prompt>: to start with we will narrow our focus on {file_name} "
                "and think through how to change it/write it so as to fulfill the user prompt, step by step, discussing"
                " what we know, identify specifically what they want accomplished, goals and sub-goals, "
                "and any existing flaws or defects WITHOUT writing any text or code for {file_name}. "
                "Just writing up a plan of action telling the LLM to follow how to rewrite/write the file in line with "
                "this plan and stating specifically that this plan is to be replaced with actual functioning file.",

                step_two,

                "Very quickly summarize what you just wrote and where you wrote it."
            ]

            prompt_messages = analyser_messages

            for iteration, message in enumerate(prompt_messages, start=1):
                emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

                if iteration == 1:
                    response = self._chat_step(
                        iteration=iteration,
                        process_question=process_question,
                        message=message,
                        file_references=file_references or [],
                        selected_message_ids=selected_message_ids or [],
                        streaming=False,
                        model=model,
                    )
                    logging.info("Iteration %d completed with response: %s", iteration, response)

                elif iteration == 2:
                    response = self._save_file_step(
                        iteration=iteration,
                        process_question=process_question,
                        message=message,
                        file_references=file_references or [],
                        file_name=file_name,
                        model=model,
                    )

                elif iteration == 3:
                    response = self._chat_step(
                        iteration=iteration,
                        process_question=process_question,
                        message=message,
                        file_references=file_references or [],
                        selected_message_ids=selected_message_ids or [],
                        streaming=True,
                        model=model,
                    )
                    logging.info("Iteration %d completed, streaming workflow completion summary", iteration)

                emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})

        return response
