from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.PersonaConstants import SAVE_TO, TYPE, TASKS, REFERENCE, INSTRUCTION, \
    meta_analysis_filename, execution_logs_filename, DEFAULT_REQUIRED_KEYS


EditorTasks = {
    "REWRITE": "REWRITE",
    "REWRITE_FILE": "REWRITE_FILE",
    "REGEX_REFACTOR": "REGEX_REFACTOR"
}


EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS = f"""
Your role is to analyze file inputs against reference files and build upon them until the task is complete. 
Output should follow a precise JSON format, focusing on a logical task sequence. For example, create files with 'APPEND'
 before modifying them. Only modify existing files; if none are provided, indicate an error.

Specific Task Instructions:
'{EditorTasks["REGEX_REFACTOR"]}': Ensure '{PersonaConstants.INSTRUCTION}' replaces content in 
'{PersonaConstants.REWRITE_THIS}' precisely. Stick to one refactor per task.

Task Requirements:
- Logical Sequence: Organize tasks logically, creating files before modifying them.
- Existing Files: Modify only existing files; note errors if no files are provided.
- Practical Output: Keep output relevant to the document’s purpose.
- No Overwriting: Avoid unnecessary overwriting of valid content.
- Supplementary Files: Note any additional files required.
"""

EDITOR_EXECUTIVE_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Assess input files for improvements and generate tasks for a editor to create and improve
    the initial solution, in line with the initial user prompt and any initial planning""",
    "parameters": {
        TYPE: "object",
        "properties": {
            TYPE: {
                TYPE: "string",
                "description": "A summarisation of what the tasks in this directive are supposed to accomplish"
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
                            "description": f"""Task type. Examples: 
                                - '{EditorTasks["REWRITE"]}' for replacing individual blocks of text by line-number.
                            Just tell the following program which file to operate on '{SAVE_TO}' and how you want the file changed
                            go into great detail and be as helpful and extensive as possible on that front
                                - '{EditorTasks["REWRITE_FILE"]}' for complete and total rewrites of the a given file.
                                -'{EditorTasks["REGEX_REFACTOR"]}' for regex replacing a single word or words with '{PersonaConstants.INSTRUCTION}' *everywhere*.
                            Exercise Caution""",
                            "enum": [EditorTasks["REWRITE"], EditorTasks["REGEX_REFACTOR"]]  # EditorTasks["REWRITE_FILE"]
                        },
                        REFERENCE: {
                            TYPE: "array",
                            "description": "List of file names with extensions, relevant to the task.",
                            "items": {TYPE: "string"}
                        },
                        "rewrite_this": {
                            TYPE: "object",
                            "description": f"""
                            The exact text you want replaced, as it appears in the initial document. 
                            Ensure the output is a valid multi-line, triple-quote string and that any special characters
                            are escaped. 
                            YOU MUST INCLUDE THIS FOR '{EditorTasks["REGEX_REFACTOR"]}' TASKS."""
                        },
                        INSTRUCTION: {
                            TYPE: "string",
                            "description": f"""
                            Clear, concise instructions for the executor in the iterative process. That is the llm that 
                            will read these instructions next.
                            Be concise, detailed, and nuanced. Refer to previous work to specify improvements for this 
                            loop.
                            For {EditorTasks["REGEX_REFACTOR"]} tasks *ONLY* write what you want to replace the 
                            '{PersonaConstants.REWRITE_THIS}' content with."""
                        },
                        SAVE_TO: {
                            TYPE: "string",
                            "description": f"""The file where the output should be saved.
                            Must reference a file from 'what_to_reference'.
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

EDITOR_LINE_REPLACEMENT_INSTRUCTIONS = """Instructions:
- Rewrite without adding new content, or removing old content; just output a modified version of the input text.
- Structure: Maintain the original structure; do not rearrange or complete sections unless explicitly instructed.
- Indentation: Preserve exact indentation; do not alter unless specified.

Output:
- Do not try and 'conclude' the given text, if you are given a start do not 'answer' it with an end, if you are given 
the end of something, don't write a beginning.
- Unless mentioned in your instructions explicitly: Provide the rewritten text only, with no comments or additional elements. 
Do not add additional code block delimiters, docstring triple quotes or language identifiers.
- Do not change the structure or content unless explicitly directed. No additional commas, triple quotes, etc.
"""

EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS = """Objective:
Identify and provide instructions for replacing specific lines of code, clearly stating the start and end lines.

*Guidelines*:
Clarity: Provide clear, concise instructions to specify the lines to be replaced.
Boundaries: Define start and end lines precisely, covering the entire relevant section (e.g., entire function for docstrings).
Context: Include necessary surrounding lines to maintain context (e.g., all quotes in a docstring).
Avoid Redundancy: Only focus on necessary changes without altering unrelated lines.
"""

EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Replace specific lines in file_name according to the given objectives. Use the provided line 
    numbers to identify the correct lines, ensuring no overlap. The start line number must always be smaller than the 
    end line number. Line numbers are 1-indexed, and changes should be made in the order they appear.""",
    "parameters": {
        "type": "object",
        "properties": {
            "changes": {
                "type": "array",
                "description": """An array of objects, each representing a replacement operation on a specific range of 
                lines in the document, a block. Each object must specify the start and end line numbers of the block, 
                as well as the instruction for *how* to rewrite the block exactly.""",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "integer",
                            "description": """The first line number of the block to be replaced (1-indexed). 
                            This must be a positive integer and smaller than the 'end' value.
                            Place at the start of the target structural element, paragraph, aside, function etc"""
                        },
                        "end": {
                            "type": "integer",
                            "description": """The last line number of the block to be replaced (1-indexed). 
                            This must be a positive integer, greater than the 'start' value, 
                            and must refer to a line within the document.
                            Place at the end of the target structural element, paragraph, aside, function etc"""
                        },
                        "instruction": {
                            "type": "string",
                            "description": "How you want these lines to be changed"
                        }
                    },
                    "required": ["start", "end", "instruction"]
                }
            }
        }
    }
}]

# ToDo: Could be good to add an example here
REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS = """
You are a skilled and professional editor tasked with rewriting a document supplied to you piece by piece. 
Your goal is to enhance each section in alignment with overall objectives without concluding the entire report.
Further pieces will be provided for additional editing.

Your output should be suitable for direct presentation to the end user, excluding notes on document improvement or future steps. 
Write continuously to ensure another LLM can easily continue from your output. Focus on preserving the style and format 
of the original document, prioritizing existing content over your personal style.

DO NOT CONCLUDE THE DOCUMENT. (!!!)

Follow 'areas_of_improvement' to enhance the file. 
You are required to overwrite an existing file, preserving as much of the original content as possible while delivering an improved version in accordance with your directives. 
Avoid using code block delimiters or language identifiers.

**Task Requirements:**

- **Blend Content**: Ensure each section fits seamlessly into the existing document without concluding any parts, as your work contributes to a larger whole.
- **Maintain Consistency**: Ensure uniformity throughout your writing, avoiding unnecessary repetition unless summarizing explicitly.
- **Prevent Redundancy**: Avoid writing conclusions or repeating headings; ensure that content remains unique.
- **Be Specific and Detailed**: Provide clear and precise prompts.
- **Role Assignment**: Assume a specific role where necessary to guide the writing style and perspective (e.g., an environmental scientist or an economic analyst).
- **Structured Approach**: Break down complex tasks into clear, sequential steps. Provide context and ensure understanding of the broader topic.
- **Focus**: Concentrate on one task per prompt to maintain clarity and precision.
- **Use of Examples**: Include examples or templates to guide the response.
- **Continuous Refinement**: Continuously refine and iterate your prompts based on the outputs received.
- **Headings**: Ensure headings are written on new lines, write EACH new heading on a new line even at the start of your response.
"""
