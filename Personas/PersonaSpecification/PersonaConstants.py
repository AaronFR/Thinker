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
                "description": """An array of objects that you want to look up/cross reference against the
                 encyclopedia definition, including what *specifically* you want to know about that concept.
                 Can be 0 or more entries depending on context. None can be completely valid.""",
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
                "description": "An array of objects representing information you want to add to the users encyclopedia "
                               "data, be selective, only include things if they mention new information which could be "
                               "useful for further prompts down the line",
                "items": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": "A term you want to add to the users encyclopedia file, *can* include "
                                           "subsections, so user/name if the user tells you their name for example"
                        },
                        "content": {
                            "type": "string",
                            "description": "The information you want to write down, strictly to the point will filled "
                                           "with as much useful detail as possible/necessary"
                        }
                    },
                    "required": ["term", "content"]
                }
            }
        }
    }
}]
