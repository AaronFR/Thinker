from typing import Tuple

from Personas.PersonaSpecification.PersonaConstants import TYPE

SELECT_FILES_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": f"""Select from all above files given their summaries, which are appropriate for the given input.
    Be VERY selective, only include files if they explicitly relate to the given prompt. If a file has no relation or
    is only tangentially related to a given prompt DO NOT INCLUDE IT.
    By default your instinct should be to NOT INCLUDE A FILE""",
    "parameters": {
        TYPE: "object",
        "properties": {
            "files": {
                TYPE: "array",
                "description": "A list of tasks file names to hand over",
                "items": {
                    TYPE: "string",
                    "description": """File names, name with extension"""
                }
            }
        }
    }
}]



