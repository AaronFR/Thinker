from typing import List


def generate_chat_workflow(initial_message: str, file_references: List[str], selected_messages: List[str], model: str):
    return {
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


def generate_write_workflow(initial_message: str, file_references: List[str], selected_messages: List[str], model: str):
    return {
        "version": "1.0",
        "workflow_name": "Write Workflow",
        "steps": [
            {
                "step_id": 1,
                "module": "Planning response",
                "description": "Plan out a solution to the given prompt",
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
                    "file_name": "pending..",
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


WRITE_TESTS_WORKFLOW = {
    "version": "1.0",
    "workflow_name": "write_tests_workflow",
    "steps": [
        {
            "step_id": 1,
            "module": "generate_file_name",
            "description": "Generate a file name for the tests",
            "parameters": {
                "initial_message": "initial_message"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 2,
            "module": "write_tests",
            "description": "Write the tests to the assigned test file",
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
            "module": "summarize_tests",
            "description": "Summarising the tests written",
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
) -> dict:
    """
    Generate a workflow dictionary for writing pages with dynamic steps based on page count.

    :param initial_message: The initial message provided by the user.
    :param page_count: The number of pages to generate 'Save to File' steps for.
    :param file_references: A list of file references.
    :param selected_messages: A list of selected message IDs.
    :param model: The model to be used.
    :return: A dictionary representing the workflow.
    """
    workflow = {
        "version": "1.0",
        "workflow_name": "write_pages_workflow",
        "steps": [],
        "status": "pending",
    }

    # Define Pages step
    step_id = 1
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
    for _ in range(page_count):
        save_to_file_step = {
            "step_id": step_id,
            "module": "Save to File",
            "description": "Append content to the specified file",
            "parameters": {
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
            "file_references": file_references,
            "selected_message_ids": selected_messages,
            "model": "gpt-4o-mini"
        },
        "status": "pending",
        "response": {}
    }
    workflow["steps"].append(summarise_step)

    return workflow


WRITE_PAGES_WORKFLOW = {
    "workflow_id": "wf_write_pages_001",
    "version": "1.0",
    "workflow_name": "write_pages_workflow",
    "modules": {
        "generate_file_names": {
            "action": "execute_function",
            "description": "Generate file names based on the initial message",
            "parameters": {
                "prompt": "Generate file names for writing code.",
                "initial_message": "User's guidance for writing code."
            }
        },
        "write_file": {
            "action": "process_question",
            "description": "Write or rewrite the specified file",
            "parameters_template": {
                "message": "Write/Rewrite {file_name} based on...",
                "file_references": ["{file_name}"],
                "model": "GPT-4"
            }
        },
        "write_to_file": {
            "action": "write_to_file",
            "description": "Save the written code to the file system",
            "parameters_template": {
                "file_path": "/user_id/{file_name}",
                "instruction": "{code_content}"
            }
        }
    },
    "steps": [
        {
            "step_id": 1,
            "module": "generate_file_names",
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 2,
            "module": "write_file",
            "parameters": {
                "file_name": "main.py"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 3,
            "module": "write_to_file",
            "parameters": {
                "file_name": "main.py",
                "code_content": "print('Hello, World!')"
            },
            "status": "pending",
            "response": {}
        }
    ],
    "status": "pending",
}