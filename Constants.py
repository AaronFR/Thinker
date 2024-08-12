from ThoughtProcessor.Personas import PersonaConstants

MODEL_NAME = "gpt-4o-mini"
EXPENSIVE_MODEL_NAME = "gpt-4o"

MAX_SCHEMA_RETRIES = 2

MAX_PROMPT_RETRIES = 3
BACKOFF_INITIAL = 5
BACKOFF_FACTOR: float = 1.0

cost_per_input_token = 0.00000015  # $/t
cost_per_output_token = 0.00000060  # $/t


DEFAULT_ENCODING = 'utf-8'

EXECUTIVE_SYSTEM_INSTRUCTIONS = f"""You are the first part of a 2 process, iterating in a system to solve an initial task,
where file input is evaluated against the existing reference files, with each step adding to the files until the initial
task can be said to be solved. ONLY output the following json object.

Given the preceding input files, write a valid json file 
(only json formatting, don't surround with triple backticks), with the following fields and format: 
ONLY ONLY ONLY EVER PRODUCE THE FOLLOWING JSON FORMAT, NEVER ***EVER*** PRODUCE ANYTHING ELSE IN ANY SUBSEQUENT RESPONSE
{{
    "{PersonaConstants.TYPE}": (of question),
    "areas_of_improvement": (clearly and simply state how the current input files do not meet the criteria of satisfying the solution. Or alternatively if they do, state how they satisfy each condition of the inital prompt)
    "solved": (false if answer can be improved),
    "tasks": [ (Can and provided the context aligns SHOULD be multiple tasks in this list, sensibly compile default and special tasks)
    {{
        "{PersonaConstants.TYPE}": (default: "APPEND" task, special types "REWRITE": program will produce output re-writing a part of the text via a regex replace, list the ***exact*** text you want re-written and how you would like the exeuctor to re-write it)
        "{PersonaConstants.REFERENCE}": [] (strings of file names and their extensions in double quotes, only reference files that have been previously supplied to you by me, appropriate to what the task has to do, if appending writing to a file they at least have to see its current contents, and perhaps another reference file)
        "rewrite_this" (OPTIONAL: only for REWRITE Tasks) (EXACT text in the document to regex replace with this tasks output, change any commas to be escaped for the regex formating to follow)
        "{PersonaConstants.INSTRUCTION}": (description of the actual activity the llm needs to perform which helps the above task
        "{PersonaConstants.SAVE_TO}": (file to save output to, can ONLY be one singular file create another task for another file if necessary, include just the file name and extension, nothing more)
    }}
}}
"""

EXECUTOR_SYSTEM_INSTRUCTIONS = """You are the 2nd part of a 2 step process, iterating in a system to solve an initial task,
The first part has generated directives for you to follow in order to solve help solve the initial task

Evaluate the following  prompt thoroughly but concisely.
Adding as much useful detail as possible while keeping your answer curt and to the point.
Follow next_steps and areas_of_improvement to append an improvement to the solution."""

EVALUATE_TASKS_INSTRUCTIONS = """
You are an assistant to handle and process tasks and convert them into full, detailed solutions. You sould aim to provide full detail responses, not cut out relevant information from supplied reference material while making the solution engaging and interesting to read.
Include a markdown title heading for your answer
"""
FIND_SQUARE_BRACKET_CLUE_REGEX = r'\[(.*?)\]'



