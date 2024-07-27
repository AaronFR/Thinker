import ast
import logging
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
                {"role": "system", "content": f"""Given the following input solution, evaluate it as as a valid dict, with the following fields and format: 
                'Type': (of question),
                'solved': (False if answer can be improved),
                'next_steps': (if 'solved': False)
                """},
                {"role": "user", "content": f"INITIAL QUESTION: {question}"},
                {"role": "user", "content": input_solution}
            ]
            # ToDo investigate more roles
        ).choices[0].message.content
        logging.info(f"Executive Thought: {output}")
        dict_output = ast.literal_eval(output)

        return dict_output


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
