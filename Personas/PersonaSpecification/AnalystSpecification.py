from Personas.PersonaSpecification.PersonaConstants import TYPE, INSTRUCTIONS, EDITOR, WRITER, WORKERS, \
    EXECUTOR_PERSONAS, ANALYST

ANALYST_SYSTEM_INSTRUCTIONS = """
Evaluate the effectiveness of the provided solution for the specified problem. Determine if the solution 
addresses the original prompt and report your findings in the format: Solved: True/False.

Note: This is strictly a report. Do not allow other LLMs to act upon or modify this evaluation."""

ANALYST_FUNCTION_INSTRUCTIONS = f"""You are a professional {ANALYST}. A user has requested files to be generated or 
refined. Your task is to:

- Format Plan: Structure the given plan.
- Order Workers: List workers to handle tasks. Available: {EXECUTOR_PERSONAS}.
- Detailed Instructions: Provide specific guidance for each worker, highlighting past work and areas needing 
  improvement.
- File Handling: Limit instructions to write to logs or reports unless necessary. Focus on improving and saving 
  user files and new solutions.

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
      "{INSTRUCTIONS}": "Edit the draft for clarity and correctness. Improve readability and implement all 
      plan-based revisions. Provide feedback for further edits as necessary."
    }},
    {{
      "{TYPE}": "{WRITER}",
      "{INSTRUCTIONS}": "Modify the draft based on the editor’s feedback. Ensure the final version meets 
      quality standards and user expectations."
    }},
    {{
      "{TYPE}": "{EDITOR}",
      "{INSTRUCTIONS}": "Conduct a final review to ensure accuracy and completeness. Make last changes 
      to enhance quality and presentation."
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
