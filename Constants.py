
MODEL_NAME = "gpt-4o-mini"
EXPENSIVE_MODEL_NAME = "gpt-4o"

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

EXECUTIVE_PROMPT = """Given the preceding input files, write a valid json file 
(only json formatting, don't surround with triple backticks), with the following fields and format: 
{
    "Type": (of question),
    "solved": (false if answer can be improved),
    "next_steps": (if 'solved': false)
    "areas_of_improvement": (optional, not present if solution is perfect)
    "save_to": (location the next task reading this output should save its output to, only one location at a time. If being improved its okay to overwrite a supplied file. Default: "solution.txt")
    "overwrite_file" (whether depending on context a file should be overwritten or not. Default: false)
}
"""
PROMPT_FOLLOWING_EXECUTIVE_DIRECTION = """Evaluate the following  prompt thoroughly but concisely.
Adding as much useful detail as possible while keeping your answer curt and to the point.
If there is content from a solution.txt you have been run before and previous output deemed insufficient for the reasons 
stated next. 
Follow next_steps and areas_of_improvement to append an improvement to the solution.
If you have been directed to overwrite an existing file, please maintain as much of the original content as is sensible while outputing an AUGMENTED version in line with your directives."""

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



