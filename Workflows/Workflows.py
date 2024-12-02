CHAT_WORKFLOW = {
    "workflow_id": "wf_chat_001",
    "version": "1.0",
    "workflow_name": "chat_workflow",
    "modules": {
        "process_message": {
            "action": "process_question",
            "description": "Process the user's initial prompt or message",
            "parameters_template": {
                "message": "{user_message}",
                "file_references": "{file_references}",
                "selected_message_ids": "{selected_message_ids}",
                "model": "{model}",
                "streaming": True
            }
        }
    },
    "steps": [
        {
            "step_id": 1,
            "module": "process_message",
            "parameters": {
                "user_message": "initial_message",
                "file_references": [],
                "selected_message_ids": [],
                "model": "GPT-4"
            },
            "status": "pending",
            "response": {}
        }
    ],
    "status": "pending",
    "final_response": "Chat workflow completed successfully."
}

WRITE_WORKFLOW = {
    "workflow_id": "wf_write_001",
    "version": "1.0",
    "workflow_name": "write_workflow",
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
    "final_response": "Write workflow completed successfully."
}

WRITE_TESTS_WORKFLOW = {
    "workflow_id": "wf_write_tests_001",
    "version": "1.0",
    "workflow_name": "write_tests_workflow",
    "modules": {
        "generate_file_name": {
            "action": "execute_function",
            "description": "Identify the file for which tests should be written",
            "parameters_template": {
                "prompt": "Please provide the filename (including extension) of the code for which tests should be written.",
                "initial_message": "{initial_message}"
            }
        },
        "review_test_plan": {
            "action": "process_question",
            "description": "Review the file and create a test plan",
            "parameters_template": {
                "message": "Review {file_name} in light of [{initial_message}]. What should we test? How? What should we prioritize and how should the test file be structured?",
                "file_references": "{file_references}"
            }
        },
        "write_tests": {
            "action": "process_question",
            "description": "Write a test file implementing the discussed tests",
            "parameters_template": {
                "message": "Write a test file for {file_name}, implementing the tests as we discussed. Make sure each test has robust documentation explaining the test's purpose.",
                "file_references": "{file_references}",
                "model": "{model}"
            }
        },
        "assess_edge_cases": {
            "action": "process_question",
            "description": "Generate tests for edge cases and boundary conditions",
            "parameters_template": {
                "message": "Assess edge cases and boundary conditions in {file_name}, generating appropriate tests. Present the final test cases in {file_name} and comment on coverage and areas needing additional tests.",
                "file_references": "{file_references}",
                "model": "{model}"
            }
        },
        "summarize_tests": {
            "action": "process_question",
            "description": "Summarize the generated tests and their objectives",
            "parameters_template": {
                "message": "Very quickly summarize the tests you just wrote and what specifically they aim to test.",
                "file_references": "{file_references}",
                "model": "{model}"
            }
        }
    },
    "steps": [
        {
            "step_id": 1,
            "module": "generate_file_name",
            "parameters": {
                "initial_message": "initial_message"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 2,
            "module": "review_test_plan",
            "parameters": {
                "file_name": "generated_file_name",
                "initial_message": "initial_message",
                "file_references": []
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 3,
            "module": "write_tests",
            "parameters": {
                "file_name": "generated_file_name",
                "file_references": [],
                "model": "GPT-4"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 4,
            "module": "assess_edge_cases",
            "parameters": {
                "file_name": "generated_file_name",
                "file_references": [],
                "model": "GPT-4"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 5,
            "module": "summarize_tests",
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

