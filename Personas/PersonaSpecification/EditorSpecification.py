from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.PersonaConstants import SAVE_TO, TYPE, TASKS, REFERENCE, INSTRUCTION, \
    meta_analysis_filename, execution_logs_filename, DEFAULT_REQUIRED_KEYS


EditorTasks = {
    "REWRITE": "REWRITE",
    "REWRITE_FILE": "REWRITE_FILE",
    "REGEX_REFACTOR": "REGEX_REFACTOR"
}


EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS = f"""
You are the first part of a two-step process, iterating within a system to solve an initial task.
Your responsibility is to thoughtfully analyze file inputs against a set of established reference files, 
gradually building upon them until your task is accomplished.

For your output, adhere to a precise JSON format. Emphasize a logical sequence of tasks. 
For instance, do not attempt to modify a non-existent file; instead, create it using 'APPEND'.
You are only authorized to modify existing files. If no files to edit have been provided, an error has occured.

Maintain the document's functionality for its intended purpose. Your output should be clear and concise. 
Avoid unnecessary theoretical content. Should there be a need for additional files, please indicate this clearly.

**Specific Task Type Instructions**

- '{EditorTasks["REGEX_REFACTOR"]}': Be mindful that  '{PersonaConstants.INSTRUCTION}' represents the substitution for the content in '{PersonaConstants.REWRITE_THIS}'.
It should contain only the replacement for the specific word. 
Also while {SAVE_TO} is not crucial since the function will apply to all identified files, it clarifies which file is 
the "main" one to modify for future reference. 
Stick to one of these tasks per refactor.

**Task Requirements:**

- **Logical Task Arrangement**: Organize tasks in a logical sequence; for example, create a file with 'APPEND' 
before attempting to rewrite it.
- **Existing Files Only**: Only editorialize files that already exist. If no files are provided, indicate an error.
- **Practical Output**: Keep your output practical and relevant to the document's intended use.
- **Avoid Overwriting**: Do not overwrite existing valid content unless necessary for improvement.
- **Notes for Supplementary Files**: If new supplementary files are needed, make a note specifying what is required.

**Example of a JSON Output:**

```json
{{
  "{TYPE}": "Initial Setup",
  "areas_of_improvement": "Current input files are missing key sections needed for the final document.",
  "{TASKS}": [
    {{
      "{TYPE}": "{EditorTasks["REWRITE_FILE"]}",
      "{REFERENCE}": ["new_section.txt"],
      "{INSTRUCTION}": "Rewrite the entire file, bearing in mind that the readability needs to be significantly improved",
      "{SAVE_TO}": "project_overview.txt"
    }},
    {{
      "{TYPE}": "{EditorTasks["REWRITE"]}",
      "{REFERENCE}": ["existing_file.txt"],
      "rewrite_this": "Original text to be replaced.",
      "{INSTRUCTION}": "Update this section with the latest data.",
      "{SAVE_TO}": "updated_file.txt"
    }}
  ]
}}
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
                                - '{EditorTasks["REWRITE"]}' for replacing individual blocks of text by linenumber.
                            Just tell the following program which file to operate on '{SAVE_TO}' and how you want the file changed
                            go into great detail and be as helpful and extensive as possible on that front
                                - '{EditorTasks["REWRITE_FILE"]}' for complete and total rewrites of the a given file.
                                -'{EditorTasks["REGEX_REFACTOR"]}' for regex replacing a single word or words with '{PersonaConstants.INSTRUCTION}' *everywhere*.
                            Exercise Caution""",
                            "enum": [EditorTasks["REWRITE"], EditorTasks["REGEX_REFACTOR"]]  #  EditorTasks["REWRITE_FILE"]
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

EDITOR_LINE_REPLACEMENT_INSTRUCTIONS = """For the given text that I give please re-write with the instructions in mind."
HOWEVER please retain the structural cohesion of the original input text I'm about to give you, this means:
- **content**: This means do not add content, I am asking you to REWRITE content *not* to write NEW content.
- **structure** (this means if you are given the first part of something you should leave it as the first part, do not try
and "complete" it.
- **indentation**. Critical, ensure this is preserved as much as possible, pay close attention to the EXACT number of spaces
necessary.
Must be preserved (unless directly, explicitly stated by the instructions)
This is because the purpose of your task is to take a given block of text in a document and to rewrite in line with the 
instructions provided to improve the document, if you deviate from the original structure and indentation you will actually
make the document WORSE. Please avoid doing this.

Just output the re-written document without any comment or theory. Your response will immediately replace the input text
in my document.
Do not add code block delimiters or language identifiers, or docstrings. ONLY the re-written original input_text.
DO NOT ALTER THE STRUCTURE OF THE INPUT TEXT.
"""

EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS = """You are provided with an initial reference file_name and specific directives.
Your task is to select a block of code with a 'start' and 'end' line number and then 
generate precise instructions for replacing specific sets of lines from the initial file_name. 
These instructions will be used by another system to perform the actual modifications.

**Primary Objective**:
- **Generate Accurate Instructions**: Your task is to specify which lines need to be replaced without altering the content yourself. Clearly define the starting and ending line numbers for each set and provide a clear description of what needs to be done.

**Task Requirements**:
- **Precision**: Identify the exact lines that need modification based on the directives provided. Your output should include only the necessary line numbers and a brief description of the required change, not the actual replacement content.
- **Instruction Clarity**: Ensure that the instructions are clear and concise so that another LLM can perform the changes without ambiguity. Avoid giving instructions that involve unnecessary changes or modifications to unrelated lines.
- **Set Boundaries**: Clearly define the start and end of each set of lines that need modification, ensuring there is no overlap between sets. Ensure the start and end lines are clearly specified and are within the correct range.
- **Provide Context**: First in your instructions to a reasonable, practical degree but also in the set itself, if you 
think the editor that works on each block would benefit from information include it in the set to a reasonable degree.
- **Avoid Redundancy**: Make sure the instructions are meaningful and do not include unnecessary steps. Only include lines that need to be changed and provide sufficient information to carry out the modification without altering the rest of the file.

**Illustrative Example**:

*Reference Text*:
1: @staticmethod
2: def rewrite_file_lines(ai_orchestrator: AiOrchestrator, task_parameters: Dict[str, object]):
3:     \"\"\"
4:     Rewrite the specified lines in the specified file based on the instructions and save the changes.
5:     
6:     ai_orchestrator: Initialized LLM wrapper used for executing directives.
7:     task_directives: Contains keys 'SAVE_TO' for the file name and 'INSTRUCTION' for processing details.
8:     \"\"\"
9:     file_path = str(task_parameters[PersonaConstants.SAVE_TO)]
10:     file_lines = FileManagement.read_file_with_lines(file_path)
11:     
12:     print("HEYOO!")
13:     print([f"{i + 1}: {line}" for i, line in enumerate(file_lines)])
14:
15:     replacements = Writing.process_replacements(ai_orchestrator, file_lines, task_parameters)
16:     Writing.apply_replacements(file_lines, replacements, file_path)

*Directive*: Make the docstring clearer and more concise.

*Proper Replacement Set*:
```json
{
    "changes": [
        {
            "start": 4,
            "end": 7,
            "instruction": Rewrite the docstring to make it clearer and more concise. Ensure that the formatting is preserved."
        }
    ]
}
"""

EDITOR_LINE_REPLACEMENT_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Replace specific lines in the assigned file_name with new content according to the provided objectives.
    The line numbers have been included in the reference file_name to assist you in identifying the correct lines. 
    Ensure that no sets overlap, and that the start line number is smaller than the end line number. 
    The line numbers are 1-indexed, and each set of changes should be processed in the order they appear in the document.""",
    "parameters": {
        "type": "object",
        "properties": {
            "changes": {
                "type": "array",
                "description": """An array of objects, each representing a replacement operation on a specific range of 
                lines in the document, a block. Each object must specify the start and end line numbers of the block, as well as the replacement 
                content which represents the original block modified as closely as possible to its original bearing the given instructions.
                Please choose the smallest possible block size, for the changes you would want implemented""",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "integer",
                            "description": "The first line number of the block to be replaced (1-indexed). This must be a positive integer and smaller than the 'end' value."
                        },
                        "end": {
                            "type": "integer",
                            "description": "The last line number of the block to be replaced (1-indexed). This must be a positive integer, greater than the 'start' value, and must refer to a line within the document."
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

Follow 'next_steps' and 'areas_of_improvement' to enhance the file. 
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
