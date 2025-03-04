from Data.Configuration import Configuration


def load_configuration() -> str:
    """Loads code style configuration settings from the configuration module.

    :return: A formatted string containing the coding guidelines.
    """
    config = Configuration.load_config()

    return config.get("system_messages", {}).get(
        "coder_persona_message",
        f"""Following the following guidelines when writing code. Docstrings and class definitions style: reStructuredText
        indentation: 4_spaces (or typical for the language)
        max line length: 120
        imports_order: standard_libraries, then third_party_libraries finally local_imports
        Please write your code inside code blocks with language identifiers"""
    )


CODER_INSTRUCTIONS = "Analyze the user prompt in sequential order, giving priority to the most recent instructions " \
                     "provided by the user, to ensure accuracy in processing their requirements."

GENERATE_FILE_NAMES_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": "Array of filenames that should be worked on",
    "parameters": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "description": "An array of objects representing files (AT LEAST one) that you want to reference or "
                               "create in order to fulfil the given user prompt. Make sure to prioritize the creation "
                               "order: First create classes that will BE imported from first and files that will import"
                               " these classes last",
                "items": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "The complete filename (including extension) for a file you wish to "
                                           "reference or create."
                        },
                        "purpose": {
                            "type": "string",
                            "description": "A brief explanation of why the file is being referenced or created, "
                                           "clarifying its role in the overall process."
                        }
                    },
                    "required": ["file_name", "purpose"]
                }
            }
        }
    }
}]
