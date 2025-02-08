from abc import abstractmethod
from typing import Callable, Any, List

from flask_socketio import emit
from pathlib import Path

from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Configuration import Configuration
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context, add_to_expensed_nodes, get_message_context
from Utilities.Decorators import specify_functionality_context
from Utilities.ErrorHandler import ErrorHandler
from Constants.Instructions import SIMPLE_SUMMARY_PROMPT

UPDATE_WORKFLOW_STEP = "update_workflow_step"


class BaseWorkflow:
    """
    Abstract base class for all workflows.
    """

    def __init__(self):
        ErrorHandler().setup_logging()

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
    def _chat_step(
        iteration: int,
        process_prompt: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        best_of: int = 1,
        streaming: bool = True,
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
    ) -> str:
        """
        Handles individual chat steps.

        :param iteration: Current iteration number.
        :param process_prompt: Persona function to process user questions.
        :param message: The message to process.
        :param file_references: Optional references to files.
        :param selected_message_ids: Optional selected message IDs for context.
        :param best_of: how many times to run the prompt and filter for best prompt
        :param streaming: Whether to stream the response.
        :param model: The AI model to use.
        :return: AI's response.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

        response = process_prompt(
            message,
            file_references,
            selected_message_ids,
            best_of=best_of,
            streaming=streaming,
            model=model,
        )

        BaseWorkflow.emit_step_completed_events(iteration, streaming, response)
        return response

    @staticmethod
    @specify_functionality_context("summarise_workflows")
    def _summary_step(
        iteration: int,
        process_prompt: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        best_of: int = 1,
        streaming: bool = True,
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
    ) -> str:
        """
        Summarises the results of a workflow.

        ToDo: If the message is set to be critical of the output you *could* use it with the knowledge network to automatically
        tailor the AI for the user and generally.

        :param iteration: Current iteration number.
        :param process_prompt: Persona function to process user questions.
        :param message: The message to process.
        :param file_references: Optional references to files.
        :param selected_message_ids: Optional selected message IDs for context.
        :param best_of: how many times to run the prompt and filter for best prompt
        :param streaming: Whether to stream the response.
        :param model: The AI model to use.
        :return: AI's response.
        """

        config = Configuration.load_config()

        should_summarize = config['optimization'].get("summarise", False)
        if should_summarize:
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

            summarisation_system_message = config.get('systemMessages', {}).get(
                "summarisationMessage",
                SIMPLE_SUMMARY_PROMPT
            ) + f"<initial_message>\n{message}\n</initial_message>"

            output = process_prompt(
                summarisation_system_message,
                file_references,
                selected_message_ids,
                best_of=best_of,
                streaming=streaming,
                model=model,
            )
            BaseWorkflow.emit_step_completed_events(iteration, streaming, output)
            if streaming and hasattr(output, '__iter__'):
                # If streaming and output is a generator, yield each chunk
                for chunk in output:
                    yield chunk
            else:
                # If not streaming, ensure output is a string and yield it
                yield {'content': output}
        else:
            output = "Workflow finished."
            yield {'content': output}
            yield {'stream_end': True}

    @staticmethod
    def _save_file_step(
        iteration: int,
        process_prompt: Callable,
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        file_name: str,
        best_of: int = 1,
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
        overwrite: bool = True,
        message_id: str = None,
        user_id: str = None,
    ) -> str:
        """
        Handles the process of saving files to the staging directory.

        ToDo: If chatgpt fails it shouldn't save (overwrite) the input files

        :param iteration: Current iteration number.
        :param process_prompt: Persona function to process user questions.
        :param message: The message to process.
        :param file_references: References to files.
        :param file_name: Name of the file to save including extension
        :param model: The AI model to use.
        :return: AI's response.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        if not message_id:
            message_id = get_message_context()
        if not user_id:
            user_id = get_user_context()

        add_to_expensed_nodes(message_id)
        response = process_prompt(
            message,
            file_references,
            selected_message_ids,
            best_of=best_of,
            model=model,
        )
        response = response + """
        
        """  # Otherwise if a new section is appended on it won't be on a new line

        file_path = Path(user_id).joinpath(file_name)

        StorageMethodology.select().save_file(response, str(file_path), overwrite=overwrite)

        BaseWorkflow.emit_step_completed_events(iteration, streaming=False, response=response)
        return response

    @staticmethod
    def emit_step_completed_events(iteration: int, streaming: bool, response: str):
        if streaming:
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "streaming"})
        else:
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "response": response})