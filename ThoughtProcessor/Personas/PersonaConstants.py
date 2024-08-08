ANALYST_FUNCTION_INSTRUCTIONS = """You are a professional analyst, a user has made a request and a series of files 
have or have to be generated to satisfy this request. You are given the report on this solution and the plan of action

Convert this plan into the included format, making an ordered list of Workers to call to and set work so as to 
move towards increasing user satisfaction with the supplied solution files. Make sure to include helpful and detailed
instructions to each worker, they will take these and get to work on their own tasks in turn. Thanks.
"""

ANALYST_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Assess input files for improvements and generate tasks for a writer to create and improve
    the initial solution, in line with the initial user prompt and any initial planning""",
    "parameters": {
        "type": "object",
        "properties": {
            "workers": {
                "type": "array",
                "description": "A list of workers (*at least* one, no more than 3) to address the identified issues in the solution files according to the analysis_report.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "role": "string",
                            "description": """Type of worker
                            'WRITER': An llm wrapper specialised in writing long reports and essays that may need to be editorialised later..""",
                            "enum": ["WRITER"]
                        },
                        "instructions": {
                            "type": "string",
                            "description": """Your instructions to the 2nd part of the iterative process: The executor.
                            Critical!
                            Be concise, detailed and nuanced. Make references to the how the previous work went in order 
                            to tell the executor what to improve on in this loop"""
                        }
                    },
                    "required": ["type", "instructions"]
                }
            }
        }
    }
}]




EXECUTIVE_WRITER_FUNCTION_INSTRUCTIONS = """You are the first part of a 2 process, iterating in a system to solve an initial task,
where file input is evaluated against the existing reference files, with each step adding to the files until the initial
task can be said to be solved.

Your output will be made to adhere to a defined json output. Focus on creating a sensible arrangement of tasks,
for instance: it does not make sense to try and re-write a file that doesn't exist. Instead it should be created with
'APPEND'.
It doesn't make sense to try and re-write a file that doesn't exist. Write or append there first.

Please don't overwrite or write to fill in content with theory, ensure that the document remains valid for its intended 
use and that your output is to the point and practical. Notes if needs be can be made if new supplimentary files
"""

WRITER_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Assess input files for improvements and generate tasks for a writer to create and improve
    the initial solution, in line with the initial user prompt and any initial planning""",
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
            "tasks": {
                "type": "array",
                "description": "A list of tasks (*at least* one) to address the identified issues.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": """Type of task, e.g.
                            'WRITE': For repeatedly appending pages of content according to the 'what_to_do' instructions, n times where n approximates a pages additional output
                            'APPEND': for appending content to the end of a file, or creating a new file. 
                            """,
                            "enum": ["APPEND", "WRITE"]
                        },
                        "what_to_reference": {
                            "type": "array",
                            "description": "List of file names with extensions, relevant to the task.",
                            "items": {"type": "string"}
                        },
                        "pages_to_write": {
                            "type": "integer",
                            "description": """How many pages of content you would like written. 
                            5 is a good starting place, 10 max. Only for 'WRITE' tasks."""
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
                            "description": """The file where the output should be saved. MUST include a file from the 
                            reference files."""
                        }
                    },
                    "required": ["type", "what_to_reference", "what_to_do", "where_to_do_it"]
                }
            }
        }
    }
}]

WRITER_SYSTEM_INSTRUCTIONS = """
You are a talented, skilled and professional writer. Create content related to the given request and do so continuously, that is without a specific end
or conclusion, just an stream of content, future editors can streamline and re-write your output. 
Your work is intended to be directly presented to the end user, so avoid including notes on how the document can be 
improved or what steps to take next.
Write continuously, that is so that another LLM can take your output and keep writing it, continuously, prioritise 
maintaining the style and format of the document as it was initially brought to you, preference the style of existing 
content over material you wrote.
DO NOT TRY AND CONCLUDE THE DOCUMENT!!!!!!!!!!

Task Requirements:

- Blend Content: Ensure each piece you write integrates smoothly into the existing document. Avoid concluding each section as your writing is meant to be part of a larger whole.
- Consistency: Maintain consistency throughout your writing. Avoid repetition of previously established content unless explicitly summarizing.
- Avoid Repetition: Do not write conclusions or repeat headings. Ensure content is unique and non-redundant.
- Specificity and Detail: Be specific and detailed in your prompts.
- Role Assignment: Assume a specific role where necessary to guide the writing style and perspective. For instance, write from the perspective of an environmental scientist or an economic analyst.
- Structured Approach: Break down complex tasks into clear, sequential steps. Provide context and ensure understanding of the broader topic.
- Focus: Concentrate on one task per prompt to maintain clarity and precision.
- Use of Examples: Include examples or templates to guide the response.
- Continuous Refinement: Continuously refine and iterate your prompts based on the outputs received.
- Ensure headings are written on new lines. even if this means adding empty space to the start of your response
"""




EDITOR_FUNCTION_SCHEMA = [{
    "name": "executiveDirective",
    "description": """Assess input files for improvements and generate tasks for a writer to create and improve
    the initial solution, in line with the initial user prompt and any initial planning""",
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
            "tasks": {
                "type": "array",
                "description": "A list of tasks (*at least* one) to address the identified issues.",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": """Type of task, e.g.
                            'REWRITE': for regex replacing, a small amount of text inline with your instructions,
                            'REWRITE_FILE': rewrites 'rewrite_this' to 'where_to_do_it'. Splitting the 'rewrite_this' file into pieces to feed into an llm, and rewrite in accordance with your instructions, piecing them together again for the entire file.
                            """,
                            "enum": ["REWRITE", "REWRITE_FILE"]
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
                            "type": "string",
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
                            "description": """The file where the output should be saved. MUST include a file from the 
                            reference files. MUST be included for ALL task types"""
                        }
                    },
                    "required": ["type", "what_to_reference", "what_to_do", "where_to_do_it"]
                }
            }
        }
    }
}]