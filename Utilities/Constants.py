from Personas.PersonaSpecification import PersonaConstants

MAX_SCHEMA_RETRIES = 2

MAX_PROMPT_RETRIES = 3
BACKOFF_INITIAL = 5
BACKOFF_FACTOR: float = 1.0


DEFAULT_ENCODING = 'utf-8'

EXECUTIVE_SYSTEM_INSTRUCTIONS = f"""You are the first part of a 2 process, iterating in a system to solve an initial task,
where file input is evaluated against the existing reference files, with each step adding to the files until the initial
task can be said to be solved. ONLY output the following json object.

Given the preceding input files, write a valid json file 
(only json formatting, don't surround with triple backticks), with the following fields and format: 
ONLY ONLY ONLY EVER PRODUCE THE FOLLOWING JSON FORMAT, NEVER ***EVER*** PRODUCE ANYTHING ELSE IN ANY SUBSEQUENT RESPONSE
SCHEMA:
{{
    "{PersonaConstants.TYPE}": (of question),
    "areas_of_improvement": (clearly and simply state how the current input files do not meet the criteria of satisfying the solution. Or alternatively if they do, state how they satisfy each condition of the initial prompt)
    "solved": (false if answer can be improved),
    "tasks": [ (Can and provided the context aligns SHOULD be multiple tasks in this list, sensibly compile default and special tasks)
    {{
        "{PersonaConstants.TYPE}": (default: "APPEND" task, special types "REWRITE": program will produce output re-writing a part of the text via a regex replace, list the ***exact*** text you want re-written and how you would like the executor to re-write it)
        "{PersonaConstants.REFERENCE}": [] (strings of file names and their extensions in double quotes, only reference files that have been previously supplied to you by me, appropriate to what the task has to do, if appending writing to a file they at least have to see its current contents, and perhaps another reference file)
        "{PersonaConstants.REWRITE_THIS}" (OPTIONAL: only for REWRITE Tasks) (EXACT text in the document to regex replace with this tasks output, change any commas to be escaped for the regex formatting to follow)
        "{PersonaConstants.INSTRUCTION}": (description of the actual activity the llm needs to perform which helps the above task
        "{PersonaConstants.SAVE_TO}": (file to save output to, can ONLY be one singular file create another task for another file if necessary, include just the file name and extension, nothing more)
    }}
}}
"""

EXECUTOR_SYSTEM_INSTRUCTIONS = """You are the second part of a two-step process. The first part has provided directives 
to help solve the initial task.
Instructions:

- Evaluate Prompt: Review the provided prompt thoroughly and concisely.
- Detail and Clarity: Add useful details while being succinct.
- Follow Directives: Use next_steps and areas_of_improvement to append the required improvements to the solution."""
