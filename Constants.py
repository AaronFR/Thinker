
MODEL_NAME = "gpt-4o-mini"
EXPENSIVE_MODEL_NAME = "gpt-4o"

request_price = 0.0

parallel_planing_tasks = {
                1: "Can you augment the following prompt? You should add in extra detail and considerations as needed: <Prompt>{initial_prompt}</Prompt>",
                2: "Can you come up with all the points and considerations that would be connected to the following prompt? Note as well what it might be inter-connected to: <Prompt>{initial_prompt}</Prompt>",
                3: "Come up with an estimate for the complexity of the work required to complete this report to satisfaction, the output should not in anyway be lacking and should be as good as possible. That is as well complexity measured in total number of prompts that would have to be sent to a current day LLM to process the task: <Prompt>{initial_prompt}</Prompt>",
                4: "Come up with some difficulties or possible mistakes you could make while evalutating this prompt, be as harsh as possible: <Prompt>{initial_prompt}</Prompt>"
}
sequential_planing_tasks = {
    5: """Evaluate the following 4 outputs and combine their output into one specific, precise format, don't skimp or summarise add *as* much tasks and tasks details as possible:\n
        <formatting_rules>
            Format your tasks into two lists, both sharing an incrementing task_id for each task.
            Do not highlight this task_id, do not make it bold do not use double-asterisks.
            <list_entry_formatting>
                This id is for each one 'Task N:' where N is an incrementing integer starting from one, this list isn't a bullet point, the list entries specifically follow this 'Task N' format
            </list_entry_formatting>
            First a 'PARALLEL TASKS:' list followed secondly by a 'SEQUENTIAL TASKS:' list:
            When creating tasks, parallel tasks can be iterated on individually and are not connected to other tasks,
            sequential tasks are by definition dependent on other tasks output, either reviewing it, editing it, making notes and observations, etc.
                <placeholder_formatting>
                    All parallel tasks should be used by at least one sequential task. All sequential tasks should reference *at least* one task, parrellel or a precedding sequential task.
                    When denoting which sequential task is connected to which parallel or prior sequential task use square brackets and the Task N, where N is the tasks number in the list, to denote a placeholder insert.
                    The placeholder insert will be automatically replaced during execution of the prompt with the entire output of the prior task- so it makes sense for these placeholders to be at the end of their respective tasks.
                    This is not explicitly written in this example, as this instruction itself is being applied HERE. An example of such would trigger a placeholder substitution of *that* tasks output.
                    Each placeholder must be explicit, 'Task 2' (with square brackets around it) will *only* reference Task 2. "'Task 3' through 'Task 7'" (remember the square brackets) will only reference files 3 and 7, the other references must be made explicetely
                </placeholder_formatting>
        </formatting_rules>

        Prior Output:
        <1>[Task 2]</1>, <2>[Task 2]</2>, <3>[Task 3]</3>, <4>[Task 4]</4> ORIGINAL PROMPT: {initial_prompt}"""
}
PLAN_FROM_PROMPT_INSTRUCTIONS = """You are an analyst program evaluating how to break big tasks down into smaller tasks, to improve the quality of the finished solution
First decide how many tasks this task should require at a minimum to execute to completion
Then determine which tasks can be executed in parrellel and which need to be executed sequentially

Also split tasks as appropriate to size: i.e. a task to review a code base is better as one task with a large context
Meanwhile tasks that involve commenting on a output file from differing perspectives and goals are better as multiple independent tasks

IF a task needs to be executed sequentially so as to access a prior tasks output, note the tasks that need to be referened in square brackets e.g. Task 3: Review [Task 2] and [Task 1]


DO NOT TRY AND SOLVE THE PROMPT.
Do not state or query theory.
Provide a list of sequential and parallel tasks as required to complete the initial prompt.
A task should be referenced in another task, finishing with the final review and finished output task.
Each task number should be unique and should denote the order of execution.

PROCESS: First make your notes and observations, then finally follow the example format below, you do not have to follow this format EXACTLY just follow the general rules
Make sure every single task is referenced *at least* once by a later task, except for the very last task in your list
Sequential Tasks: Will be the last list you will not write ANYTHING after it
PARALLEL TASKS should not reference any other file what so ever

Rules:
 - PARALLEL TASKS should not reference any other file what so ever
 - A reference should only reference a single file, e.g. '[Task 1, 2]' is invalid, where '[Task 1], [Task 2]' is not
 - REPEAT DO NOT EVER, ***EVER*** put in more than one TASK NUMBER per square bracket, ONLY [Task N] format:
    'Task i-j' is invalid, 'Task i, j, k' is invalid, 'Task i to j' is invalid ONLY ever use 'Task N' in square brackets as a reference


<example_format>
misc notes and considerations

PARALLEL TASKS:
TASK 1: [long] Review an entire code base
Task 2: [Short] Review [file.example] and give it a rating out of 10
...

SEQUENTIAL TASKS:
Task 3: Review [Task 2]
Task 4: Referring to [Task 1] edit [Task 3]
</example_format>
"""

# NOT USED
SUB_PROMPTER_INSTRUCTIONS = """
You are a prompt subdivider: Your take prompts too large to be processed in one and break them into a list of tasks. The output of the tasks will be joined together into a finished solution for the initial prompt
DO NOT TRY AND SOLVE THE PROMPT YOURSELF. Do not ask or confirm theory, each task should be practical.
If a file/s are mentioned in the initial prompt you can mention them in tasks as [file.file_type] this reference will be replaced by the contents of the file, so ideally it should be at the end of the task

You write to a stringent specified and EXACT formula.
TASKS:
1. Prompt example A
2. Prompt example B referring [file.txt]
3. Coding improvement example C for [pythonFile.py]
etc

Do not EVER deviate from this formula, e.g. DO NOT WRITE 'Task 1:', 'Task 2:', and so on.
The word 'TASKS:' MUST be included at the start
Files MUST be referenced within square brackets e.g [example.csv]
"""

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
EXECUTIVE_FUNCTIONS_SCHEME = [{
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
REWRITE_EXECUTOR_SYSTEM_INSTRUCTIONS = """You are the 2nd part of a 2 step process, iterating in a system to rewrite a section of text,
The first part has generated general directives for you to follow in order to improve the selected text for replacement

Evaluate the following  prompt thoroughly but concisely.
Adding as much useful detail as possible while keeping your answer curt and to the point.
Follow next_steps and areas_of_improvement to append an improvement to the solution.
You have been directed to overwrite an existing file, please maintain as much of the original content as is sensible while outputing an AUGMENTED version in line with your directives.

Do not add code block delimiters, don't add a language identifier"""

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



