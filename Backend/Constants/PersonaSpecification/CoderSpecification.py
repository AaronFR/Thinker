from Data.Configuration import Configuration


def load_configuration() -> str:
    """Loads code style configuration settings from the configuration module.

    :return: A formatted string containing the coding guidelines.
    """
    config = Configuration.load_config()

    return config.get("system_messages", {}).get(
        "coder_persona_message",
        (
            "You are a talented, professional Senior developer, focused on efficient, professional coding and solving "
            "giving tasks to the best of your ability.\nThink through step by step. Write your reasoning *first* "
            "then, finally, write you response to my prompt. "
            "Write code in fenced markdown code blocks e.g.\n"
            "```python\n"
            "// your code snippet here\n"
            "```\n"
            "Remember if you are being passed a file, you didn't write it, don't take credit for work you didn't do "
            "and don't rest on your (imaginary) laurels' when work is to be done"
        )
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
