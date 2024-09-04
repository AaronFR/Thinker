import logging
import os
from typing import List

import yaml

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA


class Knowing:

    persona_specification_path = os.path.join(os.path.dirname(__file__), '..', 'Personas', 'PersonaSpecification')
    instructions = "For the given prompt return an array of concepts to be searched for in an encyclopedia, the term"
    "should be as simple as possible, e.g. the actual word of the concept. You can use the 'specifics' field if there"
    "is a specific aspect of this concept you would prefer to know more about in particular"

    @staticmethod
    def search_encyclopedia(user_messages: List[str]):
        executor = AiOrchestrator()
        output = executor.execute_function(
            [Knowing.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        print(terms)

        additional_context = ()
        encyclopedia_path = os.path.join(Knowing.persona_specification_path, "Encyclopedia.yaml")
        with open(encyclopedia_path, 'r') as file:
            encyclopedia = yaml.safe_load(file)
            for term in terms:
                try:
                    additional_context += (term, encyclopedia[term['term']])
                except Exception:
                    logging.warning(f"Term not found in encyclopedia: {term['term']}")

        return str(additional_context)


if __name__ == '__main__':
    """Suggestions
    - Define Xiblic
    """

    knowing = Knowing()
    print(knowing.search_encyclopedia(["Whats the radius of the moon?"]))