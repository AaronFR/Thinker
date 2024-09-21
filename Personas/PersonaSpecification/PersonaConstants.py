ANALYST = "analyst"
WRITER = "writer"
EDITOR = "editor"

EXECUTOR_PERSONAS = [EDITOR, WRITER]

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

"""
ToDo: Documents are themselves are a powerful way of instructing the AI to follow tasks,
 but for now we will avoid this until we can trigger it more deliberately
"""
SUMMARISER_SYSTEM_INSTRUCTIONS = """Take the file input and summarise it in a few lines.
Note what the file is, what its category is, notable features.

Finally add a index of the files various parts chapters/functions etc, structurally summarising the document"""

SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Array of terms you want to know more about""",
    "parameters": {
        "type": "object",
        "properties": {
            "terms": {
                "type": "array",
                "description": """An array of objects to look up/cross-reference against the encyclopedia definitions.
                 Can be 0 or more entries depending on context; none can be completely valid.""",
                "items": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": """A term you want to look up in the encyclopedia"""
                        },
                        "specifics": {
                            "type": "string",
                            "description": "The specific property of this term your interested in."
                        }
                    },
                    "required": ["term", "specifics"]
                }
            }
        }
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
                        "term": {
                            "type": "string",
                            "description": "A term to add to the user's encyclopedia file, *can* include subsections; "
                                           "e.g., user/name."
                        },
                        "content": {
                            "type": "string",
                            "description": "The information to write down, strictly to the point and filled with "
                                           "effective detail."
                        }
                    },
                    "required": ["term", "content"]
                }
            }
        }
    }
}]
