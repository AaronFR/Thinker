# Outputs for Base System Message

Running on o1-mini
Estimated cost: $1.5 (which was lost because of the @handle_errors decorator bug 😑)

Actual usable set cost a whole dollar 🙃, but it took a whole day to review the mini so probably worth the sum


## AutoWorkflow.py

Not much value

```python
import logging
import re
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Workflows.Workflows import generate_auto_workflow


class AutoWorkflow(BaseWorkflow):
    """
    Workflow for automating a series of prompts, where each file reference is used as context for individual prompts.

    Note:
        Saving files may take some time.
    """

    @return_for_error("An error occurred during the write workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable[..., str],
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Execute all steps of the auto workflow.

        :param process_prompt: Function to process user prompts.
        :param initial_message: The user's guidance for writing code.
        :param file_references: Optional list of file references.
        :param selected_message_ids: Optional list of selected message IDs for context.
        :param tags: Optional dictionary of additional metadata.
        :return: Summary of the AI's response.
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        model = find_enum_value(tags.get("model")) if tags and tags.get("model") else ChatGptModel.DEFAULT_MODEL
        logging.info(f"Starting AutoWorkflow with file references: {file_references}")

        workflow_data = generate_auto_workflow(
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        emit("send_workflow", {"workflow": workflow_data})

        iteration = 1
        for file_reference in file_references or []:
            file_name = StorageMethodology().extract_file_name(file_reference)
            logging.info(f"Processing file reference: {file_reference} (Extracted name: {file_name})")

            prompt_message = f"{initial_message}\n\nSpecifically focus on {file_name}"
            self._save_file_step(
                iteration=iteration,
                process_prompt=process_prompt,
                message=prompt_message,
                file_references=file_references,
                selected_message_ids=selected_message_ids or [],
                file_name=file_name,
                model=model,
                overwrite=True
            )
            iteration += 1

        summary_message = (
            f"Write a very quick summary indicating that each file in {file_references} has been processed "
            f"according to the initial user message: <user_message>{initial_message}</user_message>"
        )
        summary = self._chat_step(
            iteration=iteration,
            process_prompt=process_prompt,
            message=summary_message,
            file_references=[],
            selected_message_ids=[],
            streaming=True,
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
        )

        logging.info("AutoWorkflow execution completed successfully.")
        return summary

    def _determine_pages_step(
        self,
        iteration: int,
        initial_message: str,
        page_count: int,
        model: ChatGptModel,
    ) -> List[str]:
        """
        Determine the list of pages (prompts) to be processed based on the initial message.

        :param iteration: Current iteration number.
        :param initial_message: The user's guidance for writing code.
        :param page_count: Number of pages to generate prompts for.
        :param model: The AI model to use.
        :return: List of prompt messages for each page.
        :raises Exception: If no prompt suggestions are generated.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        
        prompt = (
            "Provide a markdown list of prompts to create a series of pages based on the following user prompt. "
            "Each prompt corresponds to one 'page'. Ensure that all prompts are clear, concise, and collectively "
            "provide valid and comprehensive instructions to fully satisfy the user's needs. If necessary, "
            "think through the problem outside of the list of prompts. "
            f"I expect {page_count} prompts. No more, no less."
        )

        response = AiOrchestrator().execute(
            prompts=[prompt],
            initial_messages=[initial_message],
            model=model
        )

        pages = self.extract_markdown_list_items(response)
        if not pages:
            raise Exception("No prompt suggestions were generated by the AI.")

        logging.info(f"Pages to be created: {pages}")
        BaseWorkflow.emit_step_completed_events(iteration, streaming=False, response=response)
        return pages

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """
        Extract list items from markdown-formatted text, supporting both unordered and ordered lists.

        :param text: The text containing markdown list items.
        :return: A list of extracted list items.
        """
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'
        matches = re.findall(pattern, text, re.MULTILINE)

        # Flatten matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        logging.debug(f"Extracted markdown list items: {extracted_items}")
        return extracted_items

```

## BaseWorkflow.py

Not much to suggest

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Any, List, Dict

from flask_socketio import emit

from AiOrchestration.ChatGptModel import ChatGptModel
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error

UPDATE_WORKFLOW_STEP = "update_workflow_step"


class BaseWorkflow(ABC):
    """
    Abstract base class for all workflows.

    Provides foundational methods and structure that all specific workflows should inherit.
    """

    @abstractmethod
    def execute(self, process_prompt: Callable[..., str], **kwargs) -> Any:
        """
        Executes the workflow with the given parameters.

        :param process_prompt: Function to process user questions.
        :type process_prompt: Callable[..., str]
        :param kwargs: Additional arguments specific to the workflow.
        :type kwargs: dict
        :return: Result of the workflow execution.
        :rtype: Any
        """
        pass

    @staticmethod
    def _chat_step(
        iteration: int,
        process_prompt: Callable[..., str],
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        streaming: bool = True,
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
    ) -> str:
        """
        Handles individual chat steps within the workflow.

        Emits workflow step updates and processes the chat message using the provided prompt processor.

        :param iteration: Current iteration number.
        :type iteration: int
        :param process_prompt: Function to process user questions.
        :type process_prompt: Callable[..., str]
        :param message: The message to process.
        :type message: str
        :param file_references: References to files.
        :type file_references: List[str]
        :param selected_message_ids: Selected message IDs for context.
        :type selected_message_ids: List[str]
        :param streaming: Whether to stream the response, defaults to True.
        :type streaming: bool, optional
        :param model: The AI model to use, defaults to CHAT_GPT_4_OMNI_MINI.
        :type model: ChatGptModel, optional
        :return: AI's response.
        :rtype: str
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        response = process_prompt(
            message,
            file_references,
            selected_message_ids,
            streaming=streaming,
            model=model,
        )

        BaseWorkflow.emit_step_completed_events(iteration, streaming, response)
        return response

    @staticmethod
    def _save_file_step(
        iteration: int,
        process_prompt: Callable[..., str],
        message: str,
        file_references: List[str],
        selected_message_ids: List[str],
        file_name: str,
        model: ChatGptModel = ChatGptModel.CHAT_GPT_4_OMNI_MINI,
        overwrite: bool = True,
    ) -> str:
        """
        Handles the process of saving files within the workflow.

        Processes the provided message, saves the response to the specified file, and emits workflow step updates.

        :param iteration: Current iteration number.
        :type iteration: int
        :param process_prompt: Function to process user questions.
        :type process_prompt: Callable[..., str]
        :param message: The message to process.
        :type message: str
        :param file_references: References to files.
        :type file_references: List[str]
        :param selected_message_ids: Selected message IDs for context.
        :type selected_message_ids: List[str]
        :param file_name: Name of the file to save.
        :type file_name: str
        :param model: The AI model to use, defaults to CHAT_GPT_4_OMNI_MINI.
        :type model: ChatGptModel, optional
        :param overwrite: Whether to overwrite the existing file, defaults to True.
        :type overwrite: bool, optional
        :return: AI's response.
        :rtype: str
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        response = process_prompt(
            message,
            file_references,
            selected_message_ids,
            model=model,
        )
        response += "\n\n"  # Ensure separation for appended sections

        user_id = get_user_context()
        file_path = Path(user_id).joinpath(file_name)

        StorageMethodology.select().save_file(response, str(file_path), overwrite=overwrite)

        BaseWorkflow.emit_step_completed_events(iteration, streaming=False, response=response)
        return response

    @staticmethod
    def emit_step_completed_events(iteration: int, streaming: bool, response: str) -> None:
        """
        Emits events indicating the completion of a workflow step.

        :param iteration: Current iteration number.
        :type iteration: int
        :param streaming: Whether the response is being streamed.
        :type streaming: bool
        :param response: The response from the AI.
        :type response: str
        """
        if streaming:
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "streaming"})
        else:
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "response": response})

```

## ChatWorkflow.py

Not much use but that's the method

```python
import logging
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow
from Workflows.Workflows import generate_chat_workflow


class ChatWorkflow(BaseWorkflow):
    """
    Handles chat-based interactions with the user.

    This workflow manages the process of responding to user prompts 
    and processing any relevant file references or selected messages.
    """

    @return_for_error("An error occurred during the chat workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable[..., str],
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes the chat workflow.

        :param process_prompt: Function to process user prompts.
        :type process_prompt: Callable[..., str]
        :param initial_message: The user's initial prompt.
        :type initial_message: str
        :param file_references: Optional list of file references.
        :type file_references: Optional[List[str]], optional
        :param selected_message_ids: Optional list of selected message IDs for context.
        :type selected_message_ids: Optional[List[str]], optional
        :param tags: Optional dictionary of additional metadata.
        :type tags: Optional[Dict[str, str]], optional
        :return: AI's response.
        :rtype: str
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        logging.info("Chat workflow initiated.")

        # Safely retrieve the model from tags or use the default model
        model = (
            find_enum_value(tags.get("model")) if tags and tags.get("model") else ChatGptModel.DEFAULT_MODEL
        )
        logging.debug(f"Using model: {model.value}")

        # Generate and emit the workflow details
        workflow_details = generate_chat_workflow(
            initial_message=initial_message,
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        logging.debug(f"Generated workflow details: {workflow_details}")
        emit("send_workflow", {"workflow": workflow_details})

        # Execute the chat step
        response = self._chat_step(
            iteration=1,
            process_prompt=process_prompt,
            message=initial_message,
            file_references=file_references or [],
            selected_message_ids=selected_message_ids or [],
            streaming=True,
            model=model,
        )

        logging.info("Chat workflow executed successfully.")
        return response

```

## Instructions.py

Some improvements to the contents, the rest was complete overkill

```python
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Instructions:
    """
    A utility class for generating instruction statements for file creation and modification.

    This class provides static methods to generate formatted instructions based on user inputs.
    """

    @staticmethod
    def plan_file_creation(initial_message: str, file_name: str) -> str:
        """
        Generate a plan of action for creating or rewriting a file based on the user's initial message.

        :param initial_message: The user's initial guidance or prompt.
        :type initial_message: str
        :param file_name: The name of the file to be created or rewritten.
        :type file_name: str
        :return: A formatted instruction statement for planning file creation.
        :rtype: str
        :raises ValueError: If `initial_message` or `file_name` is empty.
        """
        if not initial_message:
            logger.error("Initial message is empty.")
            raise ValueError("Initial message cannot be empty.")
        if not file_name:
            logger.error("File name is empty.")
            raise ValueError("File name cannot be empty.")

        statement = (
            f"<user_prompt>{initial_message}</user_prompt>: To start with, we will narrow our focus on "
            f"{file_name} and think through how to change or write it to fulfill the user prompt, step by step. "
            "We will discuss what we know, identify specifically what the user wants accomplished, goals and "
            "sub-goals, and any existing flaws or defects WITHOUT writing any text or code for {file_name}. "
            "We are just writing up a plan of action instructing the LLM to follow how to rewrite or write the file "
            "in line with this plan and specifying that this plan is to be replaced with the actual functioning "
            "file."
        )

        logger.debug(f"Generated plan_file_creation statement: {statement}")
        return statement

    @staticmethod
    def write_file(file_name: str, purpose: str) -> str:
        """
        Generate an instruction statement to write or rewrite a file based on a given purpose.

        :param file_name: The name of the file to be written or rewritten.
        :type file_name: str
        :param purpose: The purpose or objective for writing the file.
        :type purpose: str
        :return: A formatted instruction statement for writing the file.
        :rtype: str
        :raises ValueError: If `file_name` or `purpose` is empty.
        """
        if not file_name:
            logger.error("File name is empty.")
            raise ValueError("File name cannot be empty.")
        if not purpose:
            logger.error("Purpose is empty.")
            raise ValueError("Purpose cannot be empty.")

        statement = (
            f"Write or rewrite {file_name} based on your previous plan of action for this particular file, "
            f"focusing on fulfilling the <purpose>{purpose}</purpose>. DO NOT OVERWRITE THIS FILE WITH A SUMMARY, "
            "do not include the contents of another file. Unless explicitly requested, the file's content must "
            "be preserved by default."
        )

        logger.debug(f"Generated write_file statement: {statement}")
        return statement

    @staticmethod
    def write_code_file(file_name: str, purpose: str) -> str:
        """
        Generate an instruction statement to write or rewrite a code file based on a given purpose.

        :param file_name: The name of the code file to be written or rewritten.
        :type file_name: str
        :param purpose: The purpose or objective for writing the code file.
        :type purpose: str
        :return: A formatted instruction statement for writing the code file.
        :rtype: str
        :raises ValueError: If `file_name` or `purpose` is empty.
        """
        if not file_name:
            logger.error("File name is empty.")
            raise ValueError("File name cannot be empty.")
        if not purpose:
            logger.error("Purpose is empty.")
            raise ValueError("Purpose cannot be empty.")

        statement = (
            f"Write or rewrite {file_name} based on your previous plan of action and the actual contents of "
            f"this particular file, focusing on fulfilling the <purpose>{purpose}</purpose>. Ensure that the file "
            "imports necessary modules, referencing the appropriate classes. DO NOT OVERWRITE THIS FILE WITH A SUMMARY, "
            "do not include the contents of another file. Unless explicitly requested, the file's content must "
            "be preserved by default."
        )

        logger.debug(f"Generated write_code_file statement: {statement}")
        return statement

```

## Workflows.py

Better

```python
import logging
from typing import List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Utilities.Decorators import return_for_error

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

UPDATE_WORKFLOW_STEP = "update_workflow_step"


def generate_chat_workflow(
    initial_message: str,
    file_references: List[str],
    selected_messages: List[str],
    model: str
) -> Dict:
    """
    Generate a workflow dictionary for chat-based interactions.

    :param initial_message: The initial message provided by the user.
    :type initial_message: str
    :param file_references: A list of file references.
    :type file_references: List[str]
    :param selected_messages: A list of selected message IDs.
    :type selected_messages: List[str]
    :param model: The model to be used.
    :type model: str
    :return: A dictionary representing the chat workflow.
    :rtype: Dict
    :raises ValueError: If any of the parameters are invalid.
    """
    logger.debug("Generating Chat Workflow.")
    
    if not initial_message:
        logger.error("Initial message is empty.")
        raise ValueError("Initial message cannot be empty.")
    if not model:
        logger.error("Model is not specified.")
        raise ValueError("Model must be specified.")

    workflow = {
        "version": "1.0",
        "workflow_name": "Chat Workflow",
        "steps": [
            {
                "step_id": 1,
                "module": "Chat",
                "description": "Respond to the prompt and any additional files or reference messages.",
                "parameters": {
                    "user_message": initial_message,
                    "file_references": file_references,
                    "selected_message_ids": selected_messages,
                    "model": model
                },
                "status": "pending",
                "response": {}
            }
        ],
        "status": "pending",
    }

    logger.info("Chat Workflow generated successfully.")
    return workflow


def generate_write_workflow(
    initial_message: str,
    file_references: List[str],
    selected_messages: List[str],
    model: str
) -> Dict:
    """
    Generate a workflow dictionary for writing operations.

    :param initial_message: The initial message provided by the user.
    :type initial_message: str
    :param file_references: A list of file references.
    :type file_references: List[str]
    :param selected_messages: A list of selected message IDs.
    :type selected_messages: List[str]
    :param model: The model to be used.
    :type model: str
    :return: A dictionary representing the write workflow.
    :rtype: Dict
    :raises ValueError: If any of the parameters are invalid.
    """
    logger.debug("Generating Write Workflow.")
    
    if not initial_message:
        logger.error("Initial message is empty.")
        raise ValueError("Initial message cannot be empty.")
    if not model:
        logger.error("Model is not specified.")
        raise ValueError("Model must be specified.")

    workflow = {
        "version": "1.0",
        "workflow_name": "Write Workflow",
        "steps": [
            {
                "step_id": 1,
                "module": "Planning Response",
                "description": "Plan out a solution to the given prompt.",
                "parameters": {
                    "user_message": initial_message,
                    "file_references": file_references,
                    "selected_message_ids": selected_messages,
                    "model": model
                },
                "status": "pending",
                "response": {}
            },
            {
                "step_id": 2,
                "module": "Writing to File",
                "description": "Write out solution as a valid file.",
                "parameters": {
                    "file_name": "pending...",
                    "model": model
                },
                "status": "pending",
                "response": {}
            },
            {
                "step_id": 3,
                "module": "Summarize",
                "description": "Quickly summarize the workflow's results.",
                "parameters": {
                    "model": "gpt-4o-mini"
                },
                "status": "pending",
                "response": {}
            }
        ],
        "status": "pending"
    }

    logger.info("Write Workflow generated successfully.")
    return workflow


WRITE_TESTS_WORKFLOW = {
    "version": "1.0",
    "workflow_name": "Write Tests Workflow",
    "steps": [
        {
            "step_id": 1,
            "module": "Generate File Name",
            "description": "Generate a file name for the tests.",
            "parameters": {
                "initial_message": "initial_message"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 2,
            "module": "Write Tests",
            "description": "Write the tests to the assigned test file.",
            "parameters": {
                "file_name": "generated_file_name",
                "file_references": [],
                "model": "GPT-4"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 3,
            "module": "Summarize Tests",
            "description": "Summarize the tests written.",
            "parameters": {
                "file_name": "generated_file_name",
                "file_references": [],
                "model": "GPT-4"
            },
            "status": "pending",
            "response": {}
        }
    ],
    "status": "pending",
    "final_response": "Write tests workflow completed successfully."
}


def generate_write_pages_workflow(
    initial_message: str,
    page_count: int,
    file_references: List[str],
    selected_messages: List[str],
    model: str
) -> Dict:
    """
    Generate a workflow dictionary for writing pages with dynamic steps based on page count.

    :param initial_message: The initial message provided by the user.
    :type initial_message: str
    :param page_count: The number of pages to generate 'Save to File' steps for.
    :type page_count: int
    :param file_references: A list of file references.
    :type file_references: List[str]
    :param selected_messages: A list of selected message IDs.
    :type selected_messages: List[str]
    :param model: The model to be used.
    :type model: str
    :return: A dictionary representing the write pages workflow.
    :rtype: Dict
    :raises ValueError: If any of the parameters are invalid.
    """
    logger.debug("Generating Write Pages Workflow.")

    if not initial_message:
        logger.error("Initial message is empty.")
        raise ValueError("Initial message cannot be empty.")
    if not model:
        logger.error("Model is not specified.")
        raise ValueError("Model must be specified.")
    if page_count < 1:
        logger.error("Page count must be at least 1.")
        raise ValueError("Page count must be at least 1.")
    if page_count > 10:
        logger.warning("Page count exceeds 10. Capping to 10.")
        page_count = 10

    workflow = {
        "version": "1.0",
        "workflow_name": "Write Pages Workflow",
        "steps": [],
        "status": "pending",
    }

    step_id = 1

    # Define Pages step
    define_pages_step = {
        "step_id": step_id,
        "module": "Define Pages",
        "description": "Writes out a list of instructions for how to write each iteration.",
        "parameters": {
            "user_message": initial_message,
            "file_references": file_references,
            "selected_message_ids": selected_messages,
            "model": model
        },
        "status": "pending",
        "response": {}
    }
    workflow["steps"].append(define_pages_step)
    step_id += 1

    # Dynamic Steps: Save to File (repeated based on page_count)
    for i in range(1, page_count + 1):
        save_to_file_step = {
            "step_id": step_id,
            "module": f"Save to File - Page {i}",
            "description": f"Append content to the specified file for page {i}.",
            "parameters": {
                "model": model
            },
            "status": "pending",
            "response": {}
        }
        workflow["steps"].append(save_to_file_step)
        step_id += 1

    # Summarize step
    summarize_step = {
        "step_id": step_id,
        "module": "Summarize",
        "description": "Quickly summarize the workflow.",
        "parameters": {
            "file_references": file_references,
            "selected_message_ids": selected_messages,
            "model": "gpt-4o-mini"
        },
        "status": "pending",
        "response": {}
    }
    workflow["steps"].append(summarize_step)

    logger.info("Write Pages Workflow generated successfully.")
    return workflow


def generate_auto_workflow(
    file_references: List[str],
    selected_messages: List[str],
    model: str
) -> Dict:
    """
    Generate a workflow dictionary for automatic processing of multiple files.

    :param file_references: A list of file references.
    :type file_references: List[str]
    :param selected_messages: A list of selected message IDs.
    :type selected_messages: List[str]
    :param model: The model to be used.
    :type model: str
    :return: A dictionary representing the auto workflow.
    :rtype: Dict
    :raises ValueError: If any of the parameters are invalid.
    """
    logger.debug("Generating Auto Workflow.")

    if not file_references:
        logger.error("File references list is empty.")
        raise ValueError("File references cannot be empty.")
    if not model:
        logger.error("Model is not specified.")
        raise ValueError("Model must be specified.")

    workflow = {
        "version": "1.0",
        "workflow_name": "Auto Workflow",
        "steps": [],
        "status": "pending",
    }

    step_id = 1

    # Dynamic Steps: Process each file
    for file_reference in file_references:
        file_name = Path(file_reference).name
        process_file_step = {
            "step_id": step_id,
            "module": f"Process {file_name}",
            "description": "Processing file in accordance with user's initial message.",
            "parameters": {
                "file_reference": file_reference,
                "selected_message_ids": selected_messages,
                "model": model
            },
            "status": "pending",
            "response": {}
        }
        workflow["steps"].append(process_file_step)
        step_id += 1

    # Summarize step
    summarize_step = {
        "step_id": step_id,
        "module": "Summarize",
        "description": "Quickly summarize the workflow.",
        "parameters": {
            "model": "gpt-4o-mini"
        },
        "status": "pending",
        "response": {}
    }
    workflow["steps"].append(summarize_step)

    logger.info("Auto Workflow generated successfully.")
    return workflow

```

## WritePagesWorkflow.py

```python
import logging
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Functionality.Writing import Writing
from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error, handle_errors
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Constants.Instructions import write_file, write_code_file, plan_file_creation
from Workflows.Workflows import generate_write_pages_workflow

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class WritePagesWorkflow(BaseWorkflow):
    """
    Workflow for writing multiple pages based on user specifications.
    
    This workflow manages the creation of multiple pages by processing 
    user instructions and generating corresponding files.
    """

    @return_for_error("An error occurred during the write pages workflow.", debug_logging=True)
    @handle_errors
    def execute(
            self,
            process_prompt: Callable[..., str],
            initial_message: str,
            file_references: Optional[List[str]] = None,
            selected_message_ids: Optional[List[str]] = None,
            tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Execute all steps of the write pages workflow.
        
        :param process_prompt: Function to process user prompts.
        :type process_prompt: Callable[..., str]
        :param initial_message: The user's guidance for writing pages.
        :type initial_message: str
        :param file_references: Optional list of file references.
        :type file_references: Optional[List[str]], optional
        :param selected_message_ids: Optional list of selected message IDs for context.
        :type selected_message_ids: Optional[List[str]], optional
        :param tags: Optional dictionary of additional metadata.
        :type tags: Optional[Dict[str, str]], optional
        :return: Summary of the AI's response.
        :rtype: str
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        logger.info("WritePagesWorkflow initiated.")

        # Retrieve and validate the AI model
        model = find_enum_value(tags.get("model")) if tags and tags.get("model") else ChatGptModel.DEFAULT_MODEL
        logger.debug(f"Selected AI Model: {model.value}")

        # Determine the number of pages to write
        page_count_str = tags.get("pages", "1") if tags else "1"
        try:
            page_count = int(page_count_str)
        except ValueError:
            logger.warning(f"Invalid page count '{page_count_str}'. Defaulting to 1.")
            page_count = 1

        if page_count > 10:
            logger.warning("Page count exceeds 10. Capping to 10 to prevent excessive resource usage.")
            page_count = 10

        # Generate and emit the workflow details
        workflow_details = generate_write_pages_workflow(
            initial_message=initial_message,
            page_count=page_count,
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        logger.debug(f"Generated workflow details: {workflow_details}")
        emit("send_workflow", {"workflow": workflow_details})

        # Determine pages based on the initial message
        iteration = 1
        pages = self._determine_pages_step(
            iteration=iteration,
            initial_message=initial_message,
            page_count=page_count,
            model=model
        )
        iteration += 1

        # Determine the file to write based on the initial message and tags
        files = Writing.determine_files(initial_message, tags)
        if not files:
            logger.error("No files determined for writing.")
            raise ValueError("No files determined for writing.")

        file = files[0]  # Only one file generated at a time
        file_name = file['file_name']
        purpose = file['purpose']
        logger.info(f"Preparing to write to file: {file_name} with purpose: {purpose}")

        # Process each page instruction
        for page_instruction in pages:
            self._save_file_step(
                iteration=iteration,
                process_prompt=process_prompt,
                message=page_instruction,
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                file_name=file_name,
                model=model,
                overwrite=False
            )
            logger.debug(f"Completed writing for iteration {iteration}.")
            iteration += 1

        # Summarize the workflow execution
        summary = self._chat_step(
            iteration=iteration,
            process_prompt=process_prompt,
            message="Very quickly summarize what you just wrote and where you wrote it.",
            file_references=[],
            selected_message_ids=[],
            streaming=True,
            model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
        )
        logger.info("WritePagesWorkflow executed successfully.")

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
        :type iteration: int
        :param initial_message: The user's guidance for writing pages.
        :type initial_message: str
        :param page_count: Number of pages to generate instructions for.
        :type page_count: int
        :param model: The AI model to use.
        :type model: ChatGptModel
        :return: List of page instruction messages.
        :rtype: List[str]
        :raises WorkflowExecutionError: If no prompt suggestions are generated.
        """
        emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})
        logger.debug("Determining pages to write.")

        prompt = (
            "Provide a Markdown list of prompts to create a series of pages based on the following user message. "
            "Each prompt corresponds to one 'page'. Ensure that all prompts are clear, concise, and collectively "
            "provide valid and comprehensive instructions to fully satisfy the user's needs. If necessary, "
            "think through the problem outside of the list of prompts. "
            f"I expect {page_count} prompts. No more, no less."
        )
        logger.debug(f"Prompt for page determination: {prompt}")

        response = AiOrchestrator().execute(
            prompts=[prompt],
            initial_messages=[initial_message],
            model=model
        )
        logger.debug(f"AI response for page determination: {response}")

        pages = self.extract_markdown_list_items(response)
        if not pages:
            logger.error("No prompt suggestions were generated by the AI.")
            raise ValueError("No prompt suggestions were generated by the AI.")

        logger.info(f"Pages to be created: {pages}")
        BaseWorkflow.emit_step_completed_events(iteration, streaming=False, response=response)
        return pages

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """
        Extract list items from markdown-formatted text, supporting both unordered and ordered lists.
        
        :param text: The text containing markdown list items.
        :type text: str
        :return: A list of extracted list items.
        :rtype: List[str]
        """
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'
        matches = re.findall(pattern, text, re.MULTILINE)
        logger.debug(f"Raw regex matches: {matches}")

        # Flatten matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        logger.debug(f"Extracted markdown list items: {extracted_items}")
        return extracted_items

```

## WriteTestsWorkflow.py

A little use but not much

```python
import logging
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.AiOrchestrator import AiOrchestrator
from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import UPDATE_WORKFLOW_STEP, BaseWorkflow


# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class WriteTestsWorkflow(BaseWorkflow):
    """
    Workflow for generating test files based on user-specified code files.

    This workflow manages the process of creating comprehensive test files by
    interacting with the user through a series of prompts and saving the
    generated tests appropriately.
    """

    @return_for_error("An error occurred during the write tests workflow.", debug_logging=True)
    def execute(
        self,
        process_prompt: Callable[..., str],
        initial_message: str,
        file_references: Optional[List[str]] = None,
        selected_message_ids: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes the write tests workflow.

        :param process_prompt: Function to process user prompts.
        :type process_prompt: Callable[..., str]
        :param initial_message: The user's guidance for writing tests.
        :type initial_message: str
        :param file_references: Optional list of file references.
        :type file_references: Optional[List[str]], optional
        :param selected_message_ids: Optional list of selected message IDs for context.
        :type selected_message_ids: Optional[List[str]], optional
        :param tags: Optional dictionary of additional metadata.
        :type tags: Optional[Dict[str, str]], optional
        :return: Summary of the AI's response.
        :rtype: str
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        logger.info("WriteTestsWorkflow initiated.")

        # Retrieve and validate the AI model
        model = find_enum_value(tags.get("model")) if tags and tags.get("model") else ChatGptModel.DEFAULT_MODEL
        logger.debug(f"Selected AI Model: {model.value}")

        # Obtain the filename for which tests need to be written
        file_name_prompt = (
            "Please provide the filename (including extension) of the code for which tests should be written. "
            "Please be concise."
        )
        logger.debug("Requesting filename from AI.")
        file_name = AiOrchestrator().execute(
            prompts=[file_name_prompt],
            initial_messages=[initial_message],
            model=model
        ).strip()

        if not file_name:
            logger.error("AI did not return a valid filename.")
            raise ValueError("AI did not return a valid filename.")

        logger.info(f"Filename received: {file_name}")

        # Define the sequence of test-related prompts
        test_prompt_messages = [
            f"Review {file_name} in light of [{initial_message}]. What should we test? How? What should we prioritize "
            f"and how should the test file be structured?",

            f"Write a test file for {file_name}, implementing the tests as we discussed. Make sure each test has robust "
            "documentation explaining the test's purpose.",

            f"Assess edge cases and boundary conditions in {file_name}, generating appropriate tests. "
            f"Present the final test cases in {file_name} and comment on coverage and areas needing additional tests.",

            "Very quickly summarize the tests you just wrote and what specifically they aim to test."
        ]

        prompt_messages = test_prompt_messages

        # Initialize response variable
        summary = ""

        # Iterate through each prompt and execute corresponding steps
        for iteration, message in enumerate(prompt_messages, start=1):
            logger.info(f"Executing step {iteration}: {message[:50]}...")  # Log first 50 chars for brevity
            emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "in-progress"})

            try:
                if iteration == 1:
                    # Step 1: Generate a plan for writing tests
                    response = self._save_file_step(
                        iteration=iteration,
                        process_prompt=process_prompt,
                        message=message,
                        file_references=file_references or [],
                        selected_message_ids=selected_message_ids or [],
                        file_name=file_name,
                        model=model,
                        overwrite=True
                    )

                elif iteration in {2, 3}:
                    # Step 2 and 3: Write tests and assess edge cases
                    response = self._chat_step(
                        iteration=iteration,
                        process_prompt=process_prompt,
                        message=message,
                        file_references=file_references or [],
                        selected_message_ids=selected_message_ids or [],
                        streaming=False,
                        model=model,
                    )

                elif iteration == 4:
                    # Step 4: Summarize the tests written
                    response = self._chat_step(
                        iteration=iteration,
                        process_prompt=process_prompt,
                        message=message,
                        file_references=[],
                        selected_message_ids=[],
                        streaming=True,
                        model=ChatGptModel.CHAT_GPT_4_OMNI_MINI
                    )

                else:
                    logger.warning(f"No handler defined for iteration {iteration}.")
                    response = ""

                emit(UPDATE_WORKFLOW_STEP, {"step": iteration, "status": "finished"})
            except Exception as e:
                logger.exception(f"Failed during step {iteration}.")
                raise e

        logger.info("WriteTestsWorkflow executed successfully.")
        return summary

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """
        Extract list items from markdown-formatted text, supporting both unordered and ordered lists.

        :param text: The text containing markdown list items.
        :type text: str
        :return: A list of extracted list items.
        :rtype: List[str]
        """
        import re
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'
        matches = re.findall(pattern, text, re.MULTILINE)
        logger.debug(f"Raw regex matches: {matches}")

        # Flatten matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        logger.debug(f"Extracted markdown list items: {extracted_items}")
        return extracted_items

```

## WriteWorkflow.py

Waste of time

```python
import logging
from pathlib import Path
from typing import Callable, Optional, List, Dict

from flask_socketio import emit

from AiOrchestration.ChatGptModel import find_enum_value, ChatGptModel
from Functionality.Coding import Coding
from Functionality.Writing import Writing

from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error
from Workflows.BaseWorkflow import BaseWorkflow, UPDATE_WORKFLOW_STEP
from Constants.Instructions import write_file, write_code_file, plan_file_creation
from Workflows.Workflows import generate_write_workflow

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class WriteWorkflow(BaseWorkflow):
    """
    Workflow for writing code based on user specifications.

    This workflow manages the process of creating code files by interacting
    with the user through a series of prompts and saving the generated code
    appropriately.
    """

    @return_for_error("An error occurred during the write workflow.", debug_logging=True)
    def execute(
            self,
            process_prompt: Callable[[str, List[str], List[str], bool, ChatGptModel], str],
            initial_message: str,
            file_references: Optional[List[str]] = None,
            selected_message_ids: Optional[List[str]] = None,
            tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Execute all steps of the write workflow.

        :param process_prompt: Function to process user prompts.
        :type process_prompt: Callable[[str, List[str], List[str], bool, ChatGptModel], str]
        :param initial_message: The user's guidance for writing code.
        :type initial_message: str
        :param file_references: Optional list of file references.
        :type file_references: Optional[List[str]], optional
        :param selected_message_ids: Optional list of selected message IDs for context.
        :type selected_message_ids: Optional[List[str]], optional
        :param tags: Optional dictionary of additional metadata.
        :type tags: Optional[Dict[str, str]], optional
        :return: Summary of the AI's response.
        :rtype: str
        :raises WorkflowExecutionError: If any step in the workflow fails.
        """
        logger.info("WriteWorkflow initiated.")

        # Retrieve and validate the AI model
        model = self._get_model(tags)
        logger.debug(f"Selected AI Model: {model.value}")

        # Generate and emit the workflow details
        workflow_details = generate_write_workflow(
            initial_message=initial_message,
            file_references=file_references or [],
            selected_messages=selected_message_ids or [],
            model=model.value
        )
        logger.debug(f"Generated workflow details: {workflow_details}")
        emit("send_workflow", {"workflow": workflow_details})

        # Determine files to write based on the initial message and tags
        files = Writing.determine_files(initial_message, tags)
        if not files:
            logger.error("No files determined for writing.")
            raise ValueError("No files determined for writing.")

        summary = ""
        for index, file in enumerate(files, start=1):
            file_name = file['file_name']
            purpose = file['purpose']
            emit(UPDATE_WORKFLOW_STEP, {"step": index, "file_name": file_name})
            user_id = get_user_context()
            file_path = Path(user_id).joinpath(file_name)

            logger.info(f"Writing code to {file_path}\nPurpose: {purpose}")

            # Step 1: Plan file creation
            plan_message = plan_file_creation(initial_message, file_name)
            self._chat_step(
                iteration=index,
                process_prompt=process_prompt,
                message=plan_message,
                file_references=file_references or [],
                selected_message_ids=selected_message_ids or [],
                streaming=False,
                model=model,
            )

            # Step 2: Write or rewrite the file
            write_message = write_code_file(file_name, purpose) if Coding.is_coding_file(file_name) else write_file(
                file_name, purpose)
            self._save_file_step(
                iteration=index + 1,
                process_prompt=process_prompt,
                message=write_message,
                file_references=[],
                selected_message_ids=[],
                file_name=file_name,
                model=model,
            )

            # Step 3: Summarize the actions taken
            summary_message = (
                "Very quickly summarize what you just wrote and where you wrote it."
            )
            summary = self._chat_step(
                iteration=index + 2,
                process_prompt=process_prompt,
                message=summary_message,
                file_references=[],
                selected_message_ids=[],
                streaming=True,
                model=ChatGptModel.CHAT_GPT_4_OMNI_MINI,
            )

        logger.info("WriteWorkflow executed successfully.")
        return summary

    @staticmethod
    def _get_model(tags: Optional[Dict[str, str]]) -> ChatGptModel:
        """
        Retrieve the AI model from tags or use the default model.

        :param tags: Dictionary containing metadata tags.
        :type tags: Optional[Dict[str, str]]
        :return: The selected AI model.
        :rtype: ChatGptModel
        """
        if tags and tags.get("model"):
            try:
                return find_enum_value(tags.get("model"))
            except ValueError:
                logger.warning(f"Invalid model '{tags.get('model')}' provided. Using default model.")
        return ChatGptModel.DEFAULT_MODEL

    @staticmethod
    def extract_markdown_list_items(text: str) -> List[str]:
        """
        Extract list items from markdown-formatted text, supporting both unordered and ordered lists.

        :param text: The text containing markdown list items.
        :type text: str
        :return: A list of extracted list items.
        :rtype: List[str]
        """
        import re
        pattern = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'
        matches = re.findall(pattern, text, re.MULTILINE)
        logger.debug(f"Raw regex matches: {matches}")

        # Flatten matches and filter out empty strings
        extracted_items = [item[0] or item[1] for item in matches if item[0] or item[1]]
        logger.debug(f"Extracted markdown list items: {extracted_items}")
        return extracted_items

```
