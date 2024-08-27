from typing import List

from Personas.PersonaSpecification.PersonaConstants import TYPE

SELECT_FILES_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": f"""Select from all above files given their summaries, which are appropriate for the given input""",
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


def build_file_query_prompt(evaluation_files: Tuple[str, str]) -> str:
    """Construct the prompt for selecting relevant files."""
    file_name_and_summary = ""
    for file_name, file_summary in evaluation_files:
        file_name_and_summary += f"\n{file_name} Summary: {file_summary}"

    return f"""From the list of files, choose which files are expressively explicitly relevant to my prompt. 
    This could be one, many, or NO files. Be cautious about including files.
    files: {evaluation_files}"""
