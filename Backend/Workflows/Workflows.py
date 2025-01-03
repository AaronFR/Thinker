import logging
from typing import List, Dict

from Data.Files.StorageMethodology import StorageMethodology


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
    :param file_references: A list of file references.
    :param selected_messages: A list of selected message IDs.
    :param model: The model to be used.
    :return: A dictionary representing the chat workflow.
    :raises ValueError: If any of the parameters are invalid.
    """

    workflow = {
        "version": "1.0",
        "workflow_name": "Chat Workflow",
        "steps": [
            {
                "step_id": 1,
                "module": "Chat",
                "description": "Respond to the prompt and any additional files or reference messages",
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
    :param file_references: A list of file references.
    :param selected_messages: A list of selected message IDs.
    :param model: The model to be used.
    :return: A dictionary representing the write workflow.
    :raises ValueError: If any of the parameters are invalid.
    """


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
                "description": "Write out solution as a valid file",
                "parameters": {
                    "file_name": "pending...",
                    "model": model
                },
                "status": "pending",
                "response": {}
            },
            {
                "step_id": 3,
                "module": "Summarise",
                "description": "Quickly summarise the workflow's results",
                "parameters": {
                    "model": "gpt-4o-mini"
                },
                "status": "pending",
                "response": {}
            }
        ],
        "status": "pending"
    }
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
            "description": "Summarising the tests written",
            "module": "Summarize Tests",
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
    :param page_count: The number of pages to generate 'Save to File' steps for.
    :param file_references: A list of file references.
    :param selected_messages: A list of selected message IDs.
    :param model: The model to be used.
    :return: A dictionary representing the write pages workflow.
    :raises ValueError: If any of the parameters are invalid.
    """
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
        "description": "Writes out a list of instructions for how to write each iteration",
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

    summarise_step = {
    # Summarize step
        "step_id": step_id,
        "module": "Summarise",
        "description": "Quickly summarise the workflow",
        "parameters": {
            "file_references": file_references,
            "selected_message_ids": selected_messages,
            "model": "gpt-4o-mini"
        },
        "status": "pending",
        "response": {}
    }
    workflow["steps"].append(summarise_step)

    return workflow


def generate_auto_workflow(
    file_references: List[str],
    selected_messages: List[str],
    model: str
) -> Dict:
    """
    Generate a workflow dictionary for automatic processing of multiple files.

    :param file_references: A list of file references.
    :param selected_messages: A list of selected message IDs.
    :param model: The model to be used.
    :return: A dictionary representing the auto workflow.
    :raises ValueError: If any of the parameters are invalid.
    """
    workflow = {
        "version": "1.0",
        "workflow_name": "Auto Workflow",
        "steps": [],
        "status": "pending",
    }

    step_id = 1

    # Dynamic Steps: Process file (repeated based on number of file references)
    for file_reference in file_references:
        file_name = StorageMethodology().extract_file_name(file_reference)
        save_to_file_step = {
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
        workflow["steps"].append(save_to_file_step)
        step_id += 1

    # Step N: Summarise
    summarise_step = {
        "step_id": step_id,
        "module": "Summarise",
        "description": "Quickly summarise the workflow",
        "parameters": {
            "model": "gpt-4o-mini"
        },
        "status": "pending",
        "response": {}
    }
    workflow["steps"].append(summarise_step)

    return workflow
