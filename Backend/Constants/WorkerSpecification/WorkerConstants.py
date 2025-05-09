ANALYST = "analyst"
WRITER = "writer"
EDITOR = "editor"

EXECUTOR_WORKERS = [EDITOR, WRITER]

TYPE = "type"
REFERENCE = "reference"
INSTRUCTION = "instruction"
INSTRUCTIONS = "instructions"
SAVE_TO = "save_to"
DEFAULT_REQUIRED_KEYS = [TYPE, REFERENCE, INSTRUCTION, SAVE_TO]

REWRITE_THIS = "rewrite_this"

TASKS = "tasks"
WORKERS = "workers"

meta_analysis_filename = "meta_analysis_report.txt"
execution_logs_filename = "execution_logs.txt"

SELECT_WORKFLOW_INSTRUCTIONS = [{
    "name": "executiveDirective",
    "description": """Given what my next task which of the following workflows is the most appropriate?
    Just select which workflow is most appropriate.""",
    "parameters": {
        TYPE: "object",
        "properties": {
            "selection": {
                "type": "string",
                "description": "The workflow that fits the input message the best",
            }
        },
        "required": ["order_id"],
        "additionalProperties": False
    }
}]

ADD_TO_ENCYCLOPEDIA_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Array of terms you want to know more about""",
    "parameters": {
        "type": "object",
        "properties": {
            "terms": {
                "type": "array",
                "description": "An array of objects representing the information to add to the user's encyclopedia data"
                               ". Be selective; only include things if they mention new information useful for further "
                               "prompts.",
                "items": {
                    "type": "object",
                    "properties": {
                        "node": {
                            "type": "string",
                            "description": "Create a concise, representative, high level and categorical node name "
                                           "focused on the topic's category to ensure uniqueness and prevent "
                                           "redundancy."
                        },
                        "parameter": {
                            "type": "string",
                            "description": "The name of the parameter content that will be attached to the node. "
                                           "Prefer simple single word paremter names"
                        },
                        "content": {
                            "type": "string",
                            "description": "Ensure the information is directly relevant to the topic at hand."
                                           "Strictly to the point and filled with effective detail."
                        }
                    },
                    "required": ["term", "content"]
                }
            }
        }
    }
}]