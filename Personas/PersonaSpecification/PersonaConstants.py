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

meta_analysis_filename = "meta_analysis_report.txt"
execution_logs_filename = "execution_logs.txt"

EXECUTIVE_WRITER_FUNCTION_INSTRUCTIONS = f"""
You are part of a two-step process to write and update a file. Your role is to evaluate input against existing reference 
files and update accordingly. Output must be in JSON format.

Key Points:
- Logical Task Arrangement: Make sure that a file is created/exists before trying to rewrite it.
- Write Only to Existing Files: Create files only if needed and specify errors if none exist.
- Practical and Relevant: Ensure output is to the point and relevant.
- Avoid Overwriting: Do not overwrite unless necessary.
- Supplementary Files: Note if additional files are needed.
- Avoid meta files like {meta_analysis_filename} or {execution_logs_filename}. No planning meetings required.

**Example of a JSON Output:**

```json
{{
  {TYPE}: "Initial Setup",
  "areas_of_improvement": "Current input files are missing key sections needed for the final document.",
  {TASKS}: [
    {{
      {TYPE}: "APPEND",
      {REFERENCE}: ["new_section.txt"],
      {INSTRUCTION}: "Create a new chapter outlining the project scope.",
      {SAVE_TO}: "new_section_chapter_2.txt"
    }},
    {{
      {TYPE}: "WRITE",
      {REFERENCE}: ["existing_file.txt"],
      "pages_to_write": 5,
      {INSTRUCTION}: "Expand this section with detailed analysis and recent data.",
      {SAVE_TO}: "detailed_analysis.txt"
    }}
  ]
}}
"""

WRITER_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": f"""Assess input files for improvements and generate tasks for a {WRITER} to create and improve
    the initial solution, in line with the initial user prompt and any initial planning""",
    "parameters": {
        TYPE: "object",
        "properties": {
            TYPE: {
                TYPE: "string",
                "description": "A summary of what the tasks in this directive are supposed to accomplish"
            },
            "areas_of_improvement": {
                TYPE: "string",
                "description": "Detailed explanation of how the current input files do not meet the criteria or how they do satisfy the conditions."
            },
            TASKS: {
                TYPE: "array",
                "description": "A list of tasks (*at least* one) to address the identified issues.",
                "items": {
                    TYPE: "object",
                    "properties": {
                        TYPE: {
                            TYPE: "string",
                            "description": """
                            Type of task, e.g., 'WRITE' for repeatedly appending pages of content or 'APPEND' for adding
                             content to the end of a file or creating a new file.""",
                            "enum": ["APPEND", "WRITE"]
                        },
                        REFERENCE: {
                            TYPE: "array",
                            "description": "List of file names with extensions, relevant to the task.",
                            "items": {TYPE: "string"}
                        },
                        "pages_to_write": {
                            TYPE: "integer",
                            "description": """Number of pages of content to be written.
                            Recommended starting place is 5 pages, with a maximum of 10 pages. Only for 'WRITE' tasks."""
                        },
                        INSTRUCTION: {
                            TYPE: "string",
                            "description": """Instructions to the executor for the iterative process. Be concise, 
                            detailed, and nuanced. Reference previous work to specify improvements for this loop."""
                        },
                        SAVE_TO: {
                            TYPE: "string",
                            "description": f"""The file where the output should be saved. MUST include a file from the 
                            reference files. 
                            Don't save to {meta_analysis_filename} or {execution_logs_filename} 
                            you don't have permission."""
                        }
                    },
                    "required": DEFAULT_REQUIRED_KEYS
                }
            }
        }
    }
}]

WRITER_SYSTEM_INSTRUCTIONS = f"""
You are a professional {WRITER}. Create content for the given request as a continuous stream. Your output will be 
refined by future editors.

DO NOT CONCLUDE THE DOCUMENT.

Key Points:

- No Conclusion: Avoid concluding the document. Write continuously.
- Blend Content: Integrate seamlessly into the existing document without ending sections.
- Consistency: Maintain consistency in style and format. Avoid repetition unless summarizing.
- Specificity: Be detailed and clear. Use specific examples or templates where needed.
- Role Assignment: Write from a specific role or perspective if required.
- Structured Approach: Break down complex tasks into clear, sequential steps and provide context.
- Focus: Address one task per prompt for clarity.
- Headings: Write headings on new lines, even if it means adding empty space.

**Example of a well-structured response:** 

---
Introduction

The impact of climate change on global agriculture is significant and multifaceted. It affects crop yields, soil health, 
and water availability.

Effects on Crop Yields

Climate change leads to unpredictable weather patterns, which can result in both droughts and floods, affecting crop 
yields negatively.

Solutions

Adopting sustainable farming practices and improving irrigation techniques can mitigate some of the adverse effects of 
climate change on agriculture.
---
"""

SELECT_WORKFLOW_INSTRUCTIONS = [{
    "name": "executiveDirective",
    "description": f"""Given what my next task which of the following workflows is the most appropriate?
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
