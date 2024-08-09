
MODEL_NAME = "gpt-4o-mini"
EXPENSIVE_MODEL_NAME = "gpt-4o"

execution_logs_filename = "execution_logs.txt"
meta_analysis_filename = "meta_analysis_report.txt"

backoff_factor: float = 1.0


EXECUTIVE_SYSTEM_INSTRUCTIONS = """You are the first part of a 2 process, iterating in a system to solve an initial task,
where file input is evaluated against the existing reference files, with each step adding to the files until the initial
task can be said to be solved. ONLY output the following json object.

Given the preceding input files, write a valid json file 
(only json formatting, don't surround with triple backticks), with the following fields and format: 
ONLY ONLY ONLY EVER PRODUCE THE FOLLOWING JSON FORMAT, NEVER ***EVER*** PRODUCE ANYTHING ELSE IN ANY SUBSEQUENT RESPONSE
{
    "type": (of question),
    "areas_of_improvement": (clearly and simply state how the current input files do not meet the criteria of satisfying the solution. Or alternatively if they do, state how they satisfy each condition of the inital prompt)
    "solved": (false if answer can be improved),
    "tasks": [ (Can and provided the context aligns SHOULD be multiple tasks in this list, sensibly compile default and special tasks)
    {
        "type": (default: "APPEND" task, special types "REWRITE": program will produce output re-writing a part of the text via a regex replace, list the ***exact*** text you want re-written and how you would like the exeuctor to re-write it)
        "what_to_reference": [] (strings of file names and their extensions in double quotes, only reference files that have been previously supplied to you by me, appropriate to what the task has to do, if appending writing to a file they at least have to see its current contents, and perhaps another reference file)
        "rewrite_this" (OPTIONAL: only for REWRITE Tasks) (EXACT text in the document to regex replace with this tasks output, change any commas to be escaped for the regex formating to follow)
        "what_to_do": (description of the actual activity the llm needs to perform which helps the above task
        "where_to_do_it: (file to save output to, can ONLY be one singular file create another task for another file if necessary, include just the file name and extension, nothing more)
    }
}
"""
EXECUTIVE_FUNCTION_INSTRUCTIONS = """You are the first part of a 2 process, iterating in a system to solve an initial task,
where file input is evaluated against the existing reference files, with each step adding to the files until the initial
task can be said to be solved.

Your output will be made to adhere to a defined json output. Focus on creating a sensible arrangement of tasks,
for instance: it does not make sense to try and re-write a file that doesn't exist. Instead it should be created with
'APPEND'.

Please don't overwrite or write to fill in content with theory, ensure that the document remains valid for its intended 
use and that your output is to the point and practical. Notes if needs be can be made if new supplimentary files
"""

"""
ToDo: extra schema to add
Tasks:
    - redo: number of times to redo a prompt filtering for quality of response, for tasks where quality is important
    - repeat: for APPEND tasks, so that large texts can be added to the output without triggering another run
"""
EXECUTIVE_FUNCTIONS_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Assess input files for improvements and generate tasks to provide a solution which completely 
    satisfied the initial user prompt""",
    "parameters": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "description": "A summarisation of what the tasks in this directive are supposed to accomplish"
            },
            "areas_of_improvement": {
                "type": "string",
                "description": "Detailed explanation of how the current input files do not meet the criteria or how they do satisfy the conditions."
            },
            "solved": {
                "type": "boolean",
                "description": "Indicates whether the issue is solved or if further action is needed."
            },
            "tasks": {
                "type": "array",
                "description": "A list of tasks (*at least* one) to address the identified issues.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": """Type of task, e.g.
                            'APPEND': for appending content to the end of a file, or creating a new file. 
                            'REWRITE': for regex replacing, a small amount of text inline with your instructions,
                            'REWRITE_FILE': rewrites 'rewrite_this' to 'where_to_do_it'. Splitting the 'rewrite_this' file into pieces to feed into an llm, and rewrite in accordance with your instructions, piecing them together again for the entire file.
                            Ideally 'rewrite_this' and 'where_to_do_it' are the same file""",
                            "enum": ["APPEND", "REWRITE", "REWRITE_FILE"]
                        },
                        "what_to_reference": {
                            "type": "array",
                            "description": "List of file names with extensions, relevant to the task.",
                            "items": {"type": "string"}
                        },
                        "rewrite_this": {
                            "type": """string""",
                            "description": """The text you want replaced, ***EXACTLY*** the same as it appears in the 
                            initial document, any deviation from the read content will cause the regex evaluation to fail. 
                            make sure the output is a valid multi-line, triple-quote string and that any commas or other special characters in 
                            python and escaped.
                            Make sure you reference and write to ('where_to_do_it') the file you want to change and that it has this line as you've written it
                            Only for 'REWRITE' tasks. DO NOT WRITE FOR 'REWRITE_FILE' TASKS!"""
                        },
                        "file_to_rewrite": {
                            "type": """string""",
                            "description": """The file including its extension that you want to rewrite.
                            Only for 'REWRITE_FILE' tasks."""
                        },
                        "what_to_do": {
                            "type": "string",
                            "description": """Your instructions to the 2nd part of the iterative process: The executor.
                            Critical!
                            Be concise, detailed and nuanced. Make references to the how the previous work went in order 
                            to tell the executor what to improve on in this loop"""
                        },
                        "where_to_do_it": {
                            "type": "string",
                            "description": "The file where the output should be saved. MUST include a file from the reference files"
                        }
                    },
                    "required": ["type", "what_to_reference", "what_to_do", "where_to_do_it"]
                }
            }
        }
    }
}]

EXECUTOR_SYSTEM_INSTRUCTIONS = """You are the 2nd part of a 2 step process, iterating in a system to solve an initial task,
The first part has generated directives for you to follow in order to solve help solve the initial task

Evaluate the following  prompt thoroughly but concisely.
Adding as much useful detail as possible while keeping your answer curt and to the point.
Follow next_steps and areas_of_improvement to append an improvement to the solution."""

EVALUATE_TASKS_INSTRUCTIONS = """
You are an assistant to handle and process tasks and convert them into full, detailed solutions. You sould aim to provide full detail responses, not cut out relevant information from supplied reference material while making the solution engaging and interesting to read.
Include a markdown title heading for your answer
"""
EDIT_PLAN_OF_ACTION = """You are a editing/review program supplied with a plan of action, 
filled with tasks to be evaluated by another program. 
You should look for references from one task on a prior task specifically and add them in if necessary. 
A placeholder is very specifically defined as a pair of square brackets, with 'Task N' inside, 
where N is an integer referring to a Task Id.
NEVER REMOVE PLACEHOLDERS FROM THE OUTPUT.
Review the supplied prompt and make any corrections/improvements that would improve the final result of the solution 
for the following initial prompt, if you can't see any improvements to be made just output the file as received,
 do not comment on your changes just make them: {initial_prompt}"""

SPLIT_LIST_INTO_ELEMENTS_REGEX = r'\d+\.\s'
ISOLATE_TASK_CONTENT_REGEX = r'(?:- )?Task (\d+):(.+?)(?=\n(?:- )?Task \d+: |\Z|$)'  # r"(?:- )?Task (\d+): (.+?)(?=\n(?:- )?Task \d+: |\Z)"
FIND_SQUARE_BRACKET_CLUE_REGEX = r'\[(.*?)\]'



