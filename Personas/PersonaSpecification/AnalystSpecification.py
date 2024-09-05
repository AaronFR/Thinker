from Personas.PersonaSpecification.PersonaConstants import TYPE, INSTRUCTIONS, EDITOR, WRITER, WORKERS, \
    EXECUTOR_PERSONAS, ANALYST

ANALYST_SYSTEM_INSTRUCTIONS = """
You are tasked with evaluating a solution's effectiveness for the given problem. Determine if the solution addresses 
the original prompt and provide a result in the format: Solved: True/False.

Note: This is a report only. Do not let other LLMs act on or modify this evaluation."""

ANALYST_FUNCTION_INSTRUCTIONS = f"""You are a professional {ANALYST}. A user has requested files to be generated or 
refined. Your task is to:

Format Plan: Convert the plan into a structured format.
Order Workers: List workers to handle tasks. Available: {EXECUTOR_PERSONAS}.
Detailed Instructions: Provide clear, actionable instructions for each worker, noting previous work and required improvements.
Initial Generation: Assign foundational tasks if the solution isn't created yet.
File Handling: Avoid instructing workers to write to execution_logs or report files unless necessary. Focus on saving or 
improving user files and new solutions.

**Example of an Ordered List of Workers:**

```json
{{
  "{WORKERS}": [
    {{
      "{TYPE}": "{WRITER}",
      "{INSTRUCTIONS}": "Develop the initial draft by incorporating key elements from the plan. Ensure that all sections
       are addressed comprehensively and align with the user's requirements."
    }},
    {{
      "{TYPE}": "{EDITOR}",
      "{INSTRUCTIONS}": "Edit the draft for clarity, coherence, and correctness. Enhance readability and ensure that all
       improvements from the plan are incorporated. Provide detailed feedback for any further revisions needed."
    }},
    {{
      "{TYPE}": "{WRITER}",
      "{INSTRUCTIONS}": "Make necessary adjustments based on the editor’s feedback. Ensure that the final version meets 
      all quality standards and user expectations."
    }},
    {{
      "{TYPE}": "{EDITOR}",
      "{INSTRUCTIONS}": "Perform a thorough review of the final document to ensure accuracy and completeness. Make final
       tweaks to enhance the overall presentation and quality."
    }}
  ]
}}"""

ANALYST_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": f"""Assess input files for improvements and generate tasks for a {WRITER} to create and improve
    the initial solution, in line with the initial user prompt and any initial planning""",
    "parameters": {
        TYPE: "object",
        "properties": {
            WORKERS: {
                TYPE: "array",
                "description": """A list of workers (*at least* one, no more than 3) to address the identified issues in 
                the solution files according to the analysis_report.""",
                "items": {
                    TYPE: "object",
                    "properties": {
                        TYPE: {
                            "role": "string",
                            "description": f"""Type of worker. 
                            '{WRITER}': An LLM wrapper specialized in writing long reports and essays that may need to be 
                            editorialized later. 
                            '{EDITOR}': LLM wrapper specialized in editing and rewriting existing files in line with 
                            provided priorities.""",
                            "enum": EXECUTOR_PERSONAS
                        },
                        INSTRUCTIONS: {
                            TYPE: "string",
                            "description": """Your instructions to the executor. Be concise, detailed, and nuanced. 
                            Reference previous work to specify improvements for this loop."""
                        }
                    },
                    "required": [TYPE, INSTRUCTIONS]
                }
            }
        }
    }
}]
