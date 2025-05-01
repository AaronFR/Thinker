import logging
from abc import abstractmethod
from typing import Callable, Any, List

from flask_socketio import emit

from AiOrchestration.AiModel import AiModel
from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Configuration import Configuration
from Functionality.Organising import Organising
from Utilities.Contexts import get_category_context, set_functionality_context
from Utilities.Decorators.Decorators import workflow_step_handler, specify_functionality_context
from Constants.Instructions import SIMPLE_SUMMARY_PROMPT

UPDATE_WORKFLOW_STEP = "update_workflow_step"


class BaseWorkflow:
    """
    Abstract base class for all workflows.
    """

    @abstractmethod
    def execute(self, process_prompt: Callable, **kwargs) -> Any:
        """
        Executes the workflow with the given parameters.

        :param process_prompt: Function to process user prompts.
        :param kwargs: Additional arguments specific to the workflow.
        :return: Result of the workflow execution.
        """
        pass

    @staticmethod
    @workflow_step_handler
    def _chat_step(
        iteration: int,
        process_prompt: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        best_of: int = 1,
        loops: int = 1,
        streaming: bool = True,
        model: AiModel = ChatGptModel.CHAT_GPT_4_POINT_ONE_NANO,
    ) -> str:
        """
        Handles individual chat steps.

        :param iteration: Current iteration number.
        :param process_prompt: Worker function to process user questions.
        :param message: The message to process.
        :param file_references: Optional references to files.
        :param selected_message_ids: Optional selected message IDs for context.
        :param best_of: how many times to run the prompt and filter for best prompt
        :param streaming: Whether to stream the response.
        :param model: The AI model to use.
        :return: AI's response.
        """

        response = process_prompt(
            message,
            file_references,
            selected_message_ids,
            best_of=best_of,
            loops=loops,
            streaming=streaming,
            model=model,
        )

        return response

    @staticmethod
    @workflow_step_handler
    @specify_functionality_context("summarise_workflows")
    def _summary_step(
        iteration: int,
        process_prompt: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        best_of: int = 1,
        loops: int = 1,
        streaming: bool = True,
        model: AiModel = None,
    ) -> str:
        """
        Summarises the results of a workflow.

        ToDo: If the message is set to be critical of the output you *could* use it with the knowledge network to automatically
        tailor the AI for the user and generally.

        :param iteration: Current iteration number.
        :param process_prompt: Worker function to process user questions.
        :param message: The message to process.
        :param file_references: Optional references to files.
        :param selected_message_ids: Optional selected message IDs for context.
        :param best_of: how many times to run the prompt and filter for best prompt
        :param streaming: Whether to stream the response.
        :param model: The AI model to use.
        :return: AI's response.
        """
        set_functionality_context("summarise_workflows")

        config = Configuration.load_config()
        should_summarize = config['workflows'].get("summarise", False)
        if not should_summarize:
            # If summarization is disabled, exit
            return

        summarisation_system_message = config.get('system_messages', {}).get(
            "summarisation_message",
            SIMPLE_SUMMARY_PROMPT
        ) + f"<initial_message>\n{message}\n</initial_message>"

        logging.info(f"Summary Step {iteration}: Calling process_prompt")

        output = process_prompt(
            summarisation_system_message,
            file_references,
            selected_message_ids,
            best_of=best_of,
            loops=loops,
            streaming=streaming,
            model=model,
        )

        logging.info(f"Summary Step {iteration}: process_prompt returned: {output}")

        yield from output

    @staticmethod
    @workflow_step_handler
    def _save_file_step(
        iteration: int,
        process_prompt: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        file_name: str,
        best_of: int = 1,
        loops: int = 1,
        model: AiModel = ChatGptModel.CHAT_GPT_4_POINT_ONE_NANO,
        overwrite: bool = True,
    ) -> str:
        """
        Handles the process of saving files to the selected category.

        ToDo: If chatgpt fails it shouldn't save (overwrite) the input files

        :param iteration: Current iteration number.
        :param process_prompt: Worker function to process user questions.
        :param message: The message to process.
        :param file_references: References to files.
        :param file_name: Name of the file to save including extension
        :param model: The AI model to use.
        :param overwrite: Whether or not any existing files should be overwrote
        :return: AI's response.
        """

        # ToDo: We'll see if this degrades quality
        message += "\nJust write the contents to be saved to the file without commentary."

        def remove_enclosing_fenced_code_block(code: str) -> str:
            """
            Code can be surrounded in a code block for formatting. However, we surround uploaded code with a code
            bracket. If the program writes a file within a singular code block this gets distorted with the LLM's
            starting code fence being included in the content.
            Instead of trying to get the LLM to understand when and when not to exactly add a code block, we just
            manually remove them if present.
            """
            trimmed = code.strip()

            if trimmed.count("```") != 2:
                return code

            lines = trimmed.splitlines()

            # Check if the first and last lines are fence lines.
            if lines and lines[0].startswith("```") and lines[-1].startswith("```"):
                # Remove the first and last line (the fenced code markers)
                inner_lines = lines[1:-1]
                return "\n".join(inner_lines)

            return code

        response = process_prompt(
            message,
            file_references,
            selected_message_ids,
            best_of=best_of,
            loops=loops,
            model=model,
        )

        response = remove_enclosing_fenced_code_block(response)
        response += "\n\n"  # Otherwise if a new section is appended on it won't be on a new line

        file_uuid = Organising.save_file(response, get_category_context(), file_name, overwrite=overwrite)
        if file_uuid:
            emit('output_file', {'file': file_uuid})

        return response

