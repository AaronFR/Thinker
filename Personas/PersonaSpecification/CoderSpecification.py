from Data.Configuration import Configuration


def load_configuration():
    config = Configuration.load_config()

    return f"""Following the following guidelines when writing code.
    All docstrings and class definitions must be written in the following style: {config['documentation']['style']}
    indentation: {config['code_style']['indentation']}
    line length: {config['code_style']['line_length']}
    imports_order: {config['code_style']['imports_order']}
    """


CODER_INSTRUCTIONS = "Just think through the question, step by step, prioritizing the most recent user prompt."

GENERATE_FILE_NAMES_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": "Array of filenames that should be worked on",
    "parameters": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "description": "An array of objects representing files (AT LEAST one) that you want to reference or "
                               "create in order to solve the given user prompt, prioritise the order sensibly, "
                               "First create classes that will BE imported from first and files that will import these "
                               "classes last",
                "items": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "The file (including extension) that you want to reference or create"
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Why you want to reference this file or create it"
                        }
                    },
                    "required": ["file_name", "purpose"]
                }
            }
        }
    }
}]
