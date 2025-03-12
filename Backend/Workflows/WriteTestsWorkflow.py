from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Utilities.Decorators.Decorators import return_for_error
from Utilities.models import find_model_enum_value
from Workflows.BaseWorkflow import UPDATE_WORKFLOW_STEP, BaseWorkflow


class WriteTestsWorkflow(BaseWorkflow):
    """
    Workflow for generating test files based on user-specified code files.

    ⚠ WIP ⚠
    """

    @return_for_error("An error occurred during the write tests workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable,
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes the write tests workflow.

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's guidance for writing tests.
        :param file_references: Optional list of file references.
        :param selected_message_ids: Optional list of selected message IDs for context.
        :param tags: Optional dictionary of additional metadata.
        :return: Summary of the AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        model = find_model_enum_value(tags.get("model") if tags else None)

        file_name_prompt = (
            "Please provide the filename (including extension) of the code for which tests should be written. "
            "Please be concise."
        )
        file_name = AiOrchestrator().execute(
            [file_name_prompt],
            [initial_message],
            model=model
        ).strip()

        test_prompt_messages = [
            f"Review {file_name} in light of [{initial_message}]. What should we test? How? What should we prioritize "
            f"and how should the test file be structured?",

            f"Write a test file for {file_name}, implementing the tests as we discussed. Make sure each test has robust "
            "documentation explaining the test's purpose.",

            f"Assess edge cases and boundary conditions in {file_name}, generating appropriate tests. "
            f"Present the final test cases in {file_name} and comment on coverage and areas needing additional tests.",

            "Very quickly summarise the tests you just wrote and what specifically they aim to test."
        ]

        prompt_messages = test_prompt_messages

        for iteration, message in enumerate(prompt_messages, start=1):
            # emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

            if iteration == 1:
                response = self._save_file_step(
                    iteration=iteration,
                    process_prompt=process_prompt,
                    message=message,
                    file_references=file_references or [],
                    file_name=file_name,
                    model=model,
                    overwrite=True
                )

            elif iteration == 2:
                response = self._summary_step(
                    iteration=iteration,
                    process_prompt=process_prompt,
                    message=message,
                    file_references=file_references or [],
                    selected_message_ids=selected_message_ids or [],
                    streaming=True,
                )

            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})

        return response
