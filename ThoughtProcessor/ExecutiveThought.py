import ast
import json
import logging
import re
from pprint import pprint
from typing import Dict

from openai import OpenAI

import Constants
import Prompter


class ExecutiveThought:

    def __init__(self):
        self.prompter = Prompter.Prompter()
        self.open_ai_client = OpenAI()

    def think(self, question: str, input_solution: str) -> Dict[str, str]:
        if not input_solution:
            input_solution = "Null"
        open_ai_client = OpenAI()
        model = Constants.MODEL_NAME

        output = open_ai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": Constants.EXECUTIVE_SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": f"INITIAL QUESTION: {question}"},
                {"role": "user", "content": "solution.txt:\nHideki Naganuma was an artist"},
                {"role": "user", "content": input_solution}
            ],
            functions=Constants.EXECUTIVE_FUNCTIONS_SCHEME,
            function_call={"name": "executiveDirective"}
            # ToDo investigate more roles
        )  # .choices[0].message.content
        logging.info(f"Executive Thought: {output}")
        function_call = output.choices[0].message.function_call
        arguments = function_call.arguments
        json_object = json.loads(arguments)

        pprint(json_object)

        return output


if __name__ == '__main__':
    executiveThought = ExecutiveThought()
    print(executiveThought.think("Who is Hideki Naganuma and what did they do?", """Hideki Naganuma is a Japanese composer and sound designer known for his work in video game music, particularly in the action and rhythm game genres. He gained prominence in the late 1990s and early 2000s, contributing significantly to the Sonic the Hedgehog series and developing a distinctive style characterized by eclectic blends of genres, including electronic, hip-hop, and jazz.

    **Background:**
    Naganuma was born on March 5, 1972, in Tokyo, Japan. He studied at the Osaka University of Arts, where he honed his skills in music composition and sound design. He was influenced by various music styles, and his passion for creating soundtracks began to reflect in his work.
    
    **Contributions:**
    Naganuma's notable contributions include:
    - **Jet Set Radio (2000)**: The soundtrack became iconic for its mix of hip-hop, funk, and rock elements, contributing greatly to the game's unique atmosphere.
    - **Jet Set Radio Future (2002)**: He continued to expand on his previous work, further refining his sound and incorporating a broader range of musical influences.
    - **Sonic Rush (2005)**: Naganuma composed key tracks for the Nintendo DS title, showcasing his ability to merge melodic hooks with fast-paced gameplay.
    - **Sonic Rush Adventure (2007)**: He continued his collaboration with the Sonic franchise, further solidifying his reputation as a prominent game composer.
    
    **Achievements:**
    - Naganuma’s music has received critical acclaim and has garnered a dedicated fanbase, particularly for its innovative and catchy arrangements.
    - His work has been featured in various media, including soundtracks and remixes that continue to resonate with fans of video game music.
    - He remains active in the gaming community, sharing insights on music production and interacting with fans through social media and events.
    
    Overall, Hideki Naganuma's impact on video game soundtracks is significant, marked by his ability to fuse genres and create memorable compositions that elevate the gaming experience."""))

# input = """
# {
#     "type": "improvement_suggestions",
#     "areas_of_improvement": "The current `ThoughtProcess.py` lacks readability and clarity due to complex method structures and insufficient documentation. It does not follow standard Python conventions for naming and commenting, making it hard for new developers to understand the flow and purpose of the code.",
#     "solved": false,
#     "tasks": [
#         {
#             "type": "REWRITE",
#             "what_to_reference": ["ThoughtProcess.py"],
#             "what_to_rewrite": "class ThoughtProcess:\n    \"\"\"\n    Class to handle the process of evaluating tasks using the Thought class.\n    \"\"\"",
#             "what_to_do": "Add a more comprehensive overview of the class purpose, including a brief explanation of its main functionalities and how it interacts with other components.",
#             "where_to_do_it": "suggestions.md"
#         },
#         {
#             "type": "REWRITE",
#             "what_to_reference": ["ThoughtProcess.py"],
#             "what_to_rewrite": "def evaluate_and_execute_task(self, task_description: str):",
#             "what_to_do": "Change the method signature to \"def evaluate_task(self, task: str):\" and simplify the function description to clearly state the task's execution procedure without excess detail.",
#             "where_to_do_it": "suggestions.md"
#         },
#         {
#             "type": "REWRITE",
#             "what_to_reference": ["ThoughtProcess.py"],
#             "what_to_rewrite": "def process_task(self, task_directives: Dict[str, str], overwrite: bool = False) -> Tuple[bool, str]:",
#             "what_to_do": "Modify the method description, separating the parameters clearly with better explanations of their purpose and potential values, including examples in the docstring.",
#             "where_to_do_it": "suggestions.md"
#         },
#         {
#             "type": "APPEND",
#             "what_to_reference": ["ThoughtProcess.py"],
#             "what_to_do": "Insert comments throughout the class methods to clarify complex logic and enhance understanding of each code block.",
#             "where_to_do_it": "suggestions.md"
#         }
#     ]
# }
# """
#
#
# cleaned_json_string = re.sub(r'^```json\s*|\s*```$', '', input.strip())
#
# # Properly escape backslashes, but leave known escape sequences intact
# def escape_backslashes(match):
#     sequence = match.group(0)
#     if sequence == '\\':
#         return '\\\\'
#     # Do not modify valid escape sequences like \n, \t, etc.
#     return sequence
#
#
# # Use a regex pattern that matches either a single backslash or known escape sequences
# cleaned_json_string = re.sub(r'(\\(?![ntbrf"])|\\\\)', escape_backslashes, cleaned_json_string)
#
# json.loads(cleaned_json_string)





















