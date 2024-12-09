from Personas.PersonaSpecification import PersonaConstants
from Personas.PersonaSpecification.PersonaConstants import SAVE_TO, TYPE, TASKS, REFERENCE, INSTRUCTION, \
    meta_analysis_filename, execution_logs_filename, DEFAULT_REQUIRED_KEYS
from Data.Configuration import Configuration


EditorTasks = {
    "REWRITE": "REWRITE",
    "REWRITE_FILE": "REWRITE_FILE",
    "REGEX_REFACTOR": "REGEX_REFACTOR"
}


def load_configuration() -> str:
    """
    Load configuration settings to guide the text editing process.

    :return: A string providing editing guidelines derived from the loaded configuration,
             including the expected tone, audience, and vocabulary focus.
    """
    config = Configuration.load_config()

    return f"""Following the following guidelines when editing text.
    general tone: {config['writing']['tone']}
    write for the following audience: {config['audience']}
    vocabulary focus: {config['preferred_vocabulary']}
    """


EDITOR_INSTRUCTIONS = "Carefully analyze the question, step by step, giving priority to the most recent user prompt. " \
                      "This means thoroughly examining requests to provide comprehensive assistance." \
                      "prioritizing the most recent user prompt."


EXECUTIVE_EDITOR_FUNCTION_INSTRUCTIONS = f"""
Your role is to analyze file inputs against reference files and building upon them to achieve task completion. 
Ensure the output adheres to a precise JSON format, focusing on a logical task sequence. For example, create files with 'APPEND' 
before making any modifications. Only update existing files; if none are provided, communicate an error.

Specific Task Instructions:
'{EditorTasks["REGEX_REFACTOR"]}': Ensure '{PersonaConstants.INSTRUCTION}' replaces content in 
'{PersonaConstants.REWRITE_THIS}' precisely. Stick to one refactor per task.

Task Requirements:
- Logical Sequence: Organize tasks logically, creating files before modifying them.
- Existing Files: Modify only existing files; note errors if no files are provided.
- Practical Output: Keep output relevant to the document’s purpose.
- No Overwriting: Avoid unnecessary overwriting of valid content.
- Supplementary Files: Document any additional files that may be necessary.
"""

EDITOR_EXECUTIVE_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": "Evaluate input files for areas of improvement and generate tasks for an editor to create and "
                   "enhance the initial solution, aligning with the original user prompt and any preliminary planning.",
    "parameters": {
        TYPE: "object",
        "properties": {
            TYPE: {
                TYPE: "string",
                "description": "Summary of the intended outcomes for the tasks associated with this directive."
            },
            "areas_of_improvement": {
                TYPE: "string",
                "description": "Detailed insights into how the current input files either fail to meet or exceed "
                               "expectations."
            },
            TASKS: {
                TYPE: "array",
                "description": "A list of tasks (*at least* one) to address the identified issues.",
                "items": {
                    TYPE: "object",
                    "properties": {
                        TYPE: {
                            TYPE: "string",
                            "description": "Task type. Examples:\n"
                                f"- '{EditorTasks['REWRITE']}' for replacing individual blocks of text by line-number. "
                                f"This should specify the file to operate on '{SAVE_TO}' and how you want the file "
                                "changed go into great detail and be as helpful and extensive as possible"
                                f"- '{EditorTasks['REWRITE_FILE']}' for complete rewrites of a specified file."
                                f"- '{EditorTasks['REGEX_REFACTOR']}' for regex replacements of particular terms with "
                                f"'{PersonaConstants.INSTRUCTION}' across the document. Caution is advised!",
                            "enum": [EditorTasks["REWRITE"], EditorTasks["REGEX_REFACTOR"], EditorTasks["REWRITE_FILE"]]
                        },
                        REFERENCE: {
                            TYPE: "array",
                            "description": "A list of relevant file names (with extensions) relevant to the task.",
                            "items": {TYPE: "string"}
                        },
                        "rewrite_this": {
                            TYPE: "object",
                            "description": "The exact text you want replaced, as it appears in the initial document. "
                                           "Ensure the output is a valid multi-line, triple-quote string and that any "
                                           "special characters are escaped. "
                                          f"THIS IS REQUIRED FOR '{EditorTasks['REGEX_REFACTOR']}' TASKS."
                        },
                        INSTRUCTION: {
                            TYPE: "string",
                            "description": f"""
                            Clear, concise instructions for the next LLM executor in the iterative process, that will 
                            read these instructions next.
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
- Indentation: Preserve exact indentation; do not alter unless explicitly instructed to.

Output:
- Do not try and 'conclude' the given text, if you are given a start do not 'answer' it with an end, if you are given 
the end of something, don't write a beginning.
- Unless mentioned in your instructions explicitly: Provide the rewritten text only, with no comments or additional elements. 
Do not add additional comments/docstrings, code block markers or language identifiers.
- Do not change the structure or content unless explicitly directed. No additional commas, triple quotes, etc.
"""

EDITOR_LINE_REPLACEMENT_FUNCTION_INSTRUCTIONS = """Objective:
Identify and provide instructions for replacing specific lines of code, clearly stating the start and end line numbers.

*Guidelines*:
- Clarity:  Ensure instructions are clear and concise in defining the lines to be replaced.
- Boundaries: Define start and end lines precisely, covering the entire relevant section (e.g., entire function for docstrings).
- Context: Include necessary surrounding lines to maintain context (e.g., all quotes in a docstring).
- Avoid Redundancy: Only focus on necessary changes without altering unrelated lines.
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
                            "description": "The first line number of the block to be replaced (1-indexed). "
                                           "This must be a positive integer and smaller than the 'end' value. It "
                                           "represents the beginning of the target structural element, whether it is a "
                                           "paragraph, aside, function etc"""
                        },
                        "end": {
                            "type": "integer",
                            "description": """The last line number of the block to be replaced (1-indexed). 
                            This must be a positive integer, greater than the 'start' value, 
                            and refer to an actual line in the document..
                            It signifies the end of the targeted structural element, paragraph, aside, function, etc."""
                        },
                        "instruction": {
                            "type": "string",
                            "description": "Precise instructions outlining how you want the specified lines altered."
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
You are an expert editor tasked with rewriting a document segment by segment. 
Your objective is to enrich each section while aligning with overall goals, without drawing conclusions for the entire report. 
Further segments will be provided for continued editing.

Your output should be formatted for clear presentation to the user—omit notes on document enhancement or potential subsequent steps. 
Write continuously to ensure another LLM can easily continue from your output. Focus on remaining faithful to the structure and format 
of the original document, prioritizing the existing content over individual stylistic input.

DO NOT CONCLUDE THE DOCUMENT. (!!!)

Use 'areas_of_improvement' to enhance the file. 
You are required to overwrite an existing file, preserving as much of the original content as possible while delivering an improved version in accordance with your directives. 
Avoid using code block delimiters or language identifiers.

**Task Requirements:**

- **Blend Content**: Ensure integration of each section within the existing document without concluding any parts, 
 allowing your contributions to fit into a larger composition.
- **Maintain Consistency**: Ensure uniformity throughout your writing, avoiding unnecessary repetition unless summarizing explicitly.
- **Prevent Redundancy**: Avoid writing conclusions or repeating headings; ensure that content remains unique.
- **Be Specific and Detailed**: Provide clear and precise prompts.
- **Role Assignment**: Assume a defined role as necessary to direct the writing style and viewpoint.
 (E.g., an environmental scientist or an economic analyst
- **Structured Approach**: Break down complex tasks into clear, sequential steps. Provide context and ensure 
 understanding of the broader topic.
- **Focus**: Concentrate on one task per prompt to maintain clarity and precision.
- **Use of Examples**: Include examples or templates to guide the response.
- **Continuous Refinement**: Continuously refine and iterate your prompts based on received outputs.
- **Headings**: Ensure that any new headings start on fresh lines, 
 with EACH new heading initiating on a new line at the start of your response.
"""
