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