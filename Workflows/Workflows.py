

TEST_WORKFLOW = {
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
        },
        {
            "step_id": 4,
            "module": "write_file",
            "parameters": {
                "file_name": "utils.py"
            },
            "status": "pending",
            "response": {}
        },
        {
            "step_id": 5,
            "module": "write_to_file",
            "parameters": {
                "file_name": "utils.py",
                "code_content": "def helper(): pass"
            },
            "status": "pending",
            "response": {}
        }
    ],
    "status": "pending",
    "final_response": "Write workflow completed successfully."
}