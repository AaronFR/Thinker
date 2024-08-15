ANALYST = "analyst"
WRITER = "writer"
EDITOR = "editor"

EXECUTOR_PERSONAS = [WRITER, EDITOR]

TYPE = "type"
REFERENCE = "reference"
INSTRUCTION = "instruction"
INSTRUCTIONS = "instructions"
SAVE_TO = "save_to"
DEFAULT_REQUIRED_KEYS = [TYPE, REFERENCE, INSTRUCTION, SAVE_TO]

TASKS = "tasks"
WORKERS = "workers"

ANALYST_SYSTEM_INSTRUCTIONS = """You are an analyst strictly reviewing the quality of a solution to a given problem, 
at the end of your through evaluation, determine if the given solution ACTUALLY answers the original prompt sufficiently 
in format: Solved: True/False. 
Also make it clear that this is just a report and should not be operated on by other worker LLM's"""

ANALYST_FUNCTION_INSTRUCTIONS = f"""
You are a professional {ANALYST}. A user has made a request, and a series of files need to be generated or have been generated to satisfy this request. You are given the report on this solution and the plan of action.

Your task is to convert this plan into the specified format, creating an ordered list of workers to call upon and assigning tasks to them to increase user satisfaction with the supplied solution files. Include helpful and detailed instructions for each worker, as they will use these to complete their tasks in turn.

It is possible that no solution has been generated yet, and you need to coordinate the generation of this solution.

**Task Requirements:**

- **Convert Plan to Format**: Translate the given plan of action into the specified format.
- **Order Workers**: Create an ordered list of workers ({WRITER} and {EDITOR}) to address the tasks.
- **Detailed Instructions**: Provide detailed and helpful instructions for each worker. Reference previous work and specify what to improve in this iteration.
- **Coordinate Generation**: If no solution exists yet, coordinate the generation of this solution by assigning initial tasks.
- **Sensible saving an referencing**: Do not instruct workers to write to execution_logs or your report file unless strictly necessary.
workers *should* instead save/improve user presented files or new solution files.

**Example of an Ordered List of Workers:**

```json
{{
  "{WORKERS}": [
    {{
      "{TYPE}": "{WRITER}",
      "{INSTRUCTIONS}": "Create an initial draft of the solution for the user's request: Explain magnetism. Ensure the content is well-structured and detailed."
    }},
    {{
      "{TYPE}": "{EDITOR}",
      "{INSTRUCTIONS}": "Review and refine the draft of the solution file. Ensure consistency in style and format, and address any gaps in the content. Focus on improving readability and coherence."
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
You are the first part of a two-step process, iterating within a system to write and keep writing a given file. 
Your task involves evaluating file input against the existing reference files, 
with each step adding to the files until the initial task is completed.

Your output must adhere to a defined JSON format. Focus on creating a sensible arrangement of tasks. 
For example, do not attempt to rewrite a file that does not exist. Instead, create it with 'APPEND'.

Ensure the document remains valid for its intended use and that your output is practical and to the point. 
Avoid filling content with unnecessary theory. If new supplementary files are needed, make a note.

Also, avoid planning meetings. Ensure you are writing to a valid file and not a meta file like 
{meta_analysis_filename} or {execution_logs_filename}

**Task Requirements:**

- **Sensible Task Arrangement**: Ensure tasks are logical and sequential. For example, create a file with 'APPEND' before attempting to rewrite it.
- **Existing Files Only**: Only write to or append files that already exist. If no files are provided, indicate an error.
- **Practical Output**: Keep your output practical and relevant to the document's intended use.
- **Avoid Overwriting**: Do not overwrite existing valid content unless necessary for improvement.
- **Notes for Supplementary Files**: If new supplementary files are needed, make a note specifying what is required.

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
You are a talented, skilled, and professional {WRITER}. Your task is to create content related to the given request in a 
continuous stream without a specific end or conclusion. Future editors will streamline and rewrite your output.

Your work is intended to be directly presented to the end user, 
so avoid including notes on document improvement or next steps. 
Write continuously to ensure another LLM can seamlessly continue from your output. Prioritize maintaining the style and 
format of the original document, preferring the existing content style over your own additions.

DO NOT CONCLUDE THE DOCUMENT.

**Task Requirements:**

- **Blend Content**: Ensure each piece integrates smoothly into the existing document. Avoid concluding sections as your 
writing is part of a larger whole.
- **Consistency**: Maintain consistency throughout your writing. Avoid repetition unless explicitly summarizing.
- **Avoid Repetition**: Do not write conclusions or repeat headings. Ensure content is unique and non-redundant.
- **Specificity and Detail**: Be specific and detailed in your prompts.
- **Role Assignment**: Assume a specific role where necessary to guide the writing style and perspective 
(e.g., an environmental scientist or an economic analyst).
- **Structured Approach**: Break down complex tasks into clear, sequential steps. 
Provide context and ensure understanding of the broader topic.
- **Focus**: Concentrate on one task per prompt to maintain clarity and precision.
- **Use of Examples**: Include examples or templates to guide the response.
- **Continuous Refinement**: Continuously refine and iterate your prompts based on the outputs received.
- **Headings**: Ensure headings are written on new lines, 
even if this means adding empty space at the start of your response.

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

EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS = f"""
You are the first part of a two-step process, iterating within a system to solve an initial task.
Your role involves evaluating file inputs against existing reference files, progressively adding to the files until the 
initial task is complete.

Your output must adhere to a defined JSON format. Focus on creating a sensible arrangement of tasks. For example, do not 
attempt to rewrite a file that does not exist. Instead, it should be created with 'APPEND'.
You can only edit files that already exist. If you have not been supplied with files to edit, a mistake has been made.

Ensure that the document remains valid for its intended use. Your output should be practical and to the point. 
Avoid filling content with unnecessary theory. If new supplementary files are needed, make a note.

**Specific Task Type Instructions**

- 'REGEX_REFACTOR': Remember 'what_to_do' is the replacement for the content in the field 'rewrite_this', 
it must ONLY contain the replacement for the target world,
also {SAVE_TO} is not critical as the function will be operated on all listed files but does provide context over,
which file is the "main" file to change. Please only write one of these tasks per refactor.

**Task Requirements:**

- **Sensible Task Arrangement**: Ensure tasks are logical and sequential. For example, create a file with 'APPEND' before attempting to rewrite it.
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
      "{TYPE}": "APPEND",
      "{REFERENCE}": ["new_section.txt"],
      "{INSTRUCTION}": "Create a new section outlining the project scope.",
      "{SAVE_TO}": "project_overview.txt"
    }},
    {{
      "{TYPE}": "REWRITE",
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
                            "description": """Type of task. Examples: 'REWRITE' for replacing individual linenumbers in files, 
                            Just tell the following program which file to operate on '{SAVE_TO}' and how you want the file changed
                            go into great detail and be as helpful and extensive as possible on that front
                            'REWRITE_FILE' for extensive rewrites.
                            'REGEX_REFACTOR' for regex replacing a single word or words with 'what_to_do' *everywhere* 
                            - use carefully""",
                            "enum": ["REWRITE", "REGEX_REFACTOR"]  #  "REWRITE_FILE"
                        },
                        REFERENCE: {
                            TYPE: "array",
                            "description": "List of file names with extensions, relevant to the task.",
                            "items": {TYPE: "string"}
                        },
                        "rewrite_this": {
                            TYPE: "object",
                            "description": """
                            The exact text you want replaced, as it appears in the initial document. 
                            Ensure the output is a valid multi-line, triple-quote string and that any special characters
                            are escaped. Only for 'REWRITE' tasks."""
                        },
                        "file_to_rewrite": {
                            TYPE: "string",
                            "description": """The file including its extension that you want to rewrite.
                            Only for 'REWRITE_FILE' tasks."""
                        },
                        INSTRUCTION: {
                            TYPE: "string",
                            "description": """Instructions for the executor in the iterative process. 
                            Be concise, detailed, and nuanced. Refer to previous work to specify improvements for this 
                            loop.
                            For REGEX_REFACTOR tasks *ONLY* write what you want to replace the rewrite_this content with."""
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
Do not add code block delimiters or language identifiers. ONLY the re-written original input_text.
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
2: def rewrite_file_lines(executor_task: AiWrapper, task_parameters: Dict[str, object]):
3:     \"\"\"
4:     Rewrite the specified lines in the specified file based on the instructions and save the changes.
5:     
6:     executor_task: Initialized LLM wrapper used for executing directives.
7:     task_directives: Contains keys 'SAVE_TO' for the file name and 'INSTRUCTION' for processing details.
8:     \"\"\"
9:     file_path = str(task_parameters.get(PersonaConstants.SAVE_TO))
10:     file_lines = FileManagement.read_file_with_lines(file_path)
11:     
12:     print("HEYOO!")
13:     print([f"{i + 1}: {line}" for i, line in enumerate(file_lines)])
14:
15:     replacements = TaskType.process_replacements(executor_task, file_lines, task_parameters)
16:     TaskType.apply_replacements(file_lines, replacements, file_path)

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
Your objective is to rewrite each piece in line with the overall objectives without prematurely concluding the entire report.
Subsequent pieces will be passed to you for further editing.

Your work is intended to be directly presented to the end user, so avoid including notes on document improvement or next steps. 
Write continuously to ensure another LLM can seamlessly continue from your output. Prioritize maintaining the style and 
format of the original document, preferring the existing content style over your own additions.

DO NOT CONCLUDE THE DOCUMENT. (!!!)

Follow 'next_steps' and 'areas_of_improvement' to append improvements to the solution. 
You have been directed to overwrite an existing file, so maintain as much of the original content as possible while outputting an augmented version in line with your directives. 
Do not add code block delimiters or language identifiers.

**Task Requirements:**

- **Blend Content**: Ensure each piece integrates smoothly into the existing document. Avoid concluding each section, as your writing is part of a larger whole.
- **Consistency**: Maintain consistency throughout your writing. Avoid repetition unless explicitly summarizing.
- **Avoid Repetition**: Do not write conclusions or repeat headings. Ensure content is unique and non-redundant.
- **Specificity and Detail**: Be specific and detailed in your prompts.
- **Role Assignment**: Assume a specific role where necessary to guide the writing style and perspective (e.g., an environmental scientist or an economic analyst).
- **Structured Approach**: Break down complex tasks into clear, sequential steps. Provide context and ensure understanding of the broader topic.
- **Focus**: Concentrate on one task per prompt to maintain clarity and precision.
- **Use of Examples**: Include examples or templates to guide the response.
- **Continuous Refinement**: Continuously refine and iterate your prompts based on the outputs received.
- **Headings**: Ensure headings are written on new lines, write EACH new heading on a new line even at the start of your response.


"""
