from Data.Configuration import Configuration


def load_configuration():
    config = Configuration.load_config()

    return f"""You aid the user to plan their day, notes and meetings
    
    tone: {config['writing']['tone']}, professional, secretarial
    """


PERSONAL_ASSISTANT_INSTRUCTIONS = "You are a helpful, organised Personal Assistant, helping the user with their given "\
                                  "instruction."\
                                  "prioritizing the most recent user prompt."

GENERATE_FILE_NAMES_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": "Array of filenames that should be worked on",
    "parameters": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "description": "An array of objects representing files (AT LEAST one) that you want to reference or "
                               "create in order to help the user with their given problem.",
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
