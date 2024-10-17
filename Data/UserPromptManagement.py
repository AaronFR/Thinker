import logging
from datetime import datetime

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Neo4jDriver import Neo4jDriver
from Utilities import Constants


class UserPromptManagement:
    def __init__(self):
        self.neo4jDriver = Neo4jDriver()
        self.executor = AiOrchestrator()
        self.prompt_id_counter = 1  # ToDo: - irrelevant

    def create_user_prompt_node(self, user_prompt, llm_response):
        timestamp = int(datetime.now().timestamp())
        prompt_id = self.prompt_id_counter
        self.prompt_id_counter += 1

        categorisation_input = "<user prompt>" + user_prompt + "</user prompt>\n" + "<response>" + \
                               llm_response + "</response>"
        categories = self.list_user_categories()
        category_data = self.executor.execute_function(
            ["Given the following prompt - response pair, categorise the data with a single word answer."
             "These are the following existent categories which *may* be appropriate: " + str(categories)],
            [categorisation_input],
            Constants.DETERMINE_CATEGORY_FUNCTION_SCHEMA
        )
        logging.info("category_data:", category_data)
        category = category_data["category"]


        create_user_prompt_query = """
        MERGE (user:USER)
        MERGE (category:CATEGORY {name: $category})
        CREATE (user_prompt:USER_PROMPT {id: $id, prompt: $prompt, response: $response, time: $time})
        MERGE (user)-[:USES]->(category)
        MERGE (user_prompt)-[:BELONGS_TO]->(category)
        RETURN user_prompt, category
        """
        parameters = {
            "id": prompt_id,
            "prompt": user_prompt,
            "response": llm_response,
            "time": timestamp,
            "category": category
        }

        result = self.neo4jDriver.execute_write(create_user_prompt_query, parameters)
        return result

    def list_user_categories(self):
        """
        List all unique categories associated with the user

        ToDo: Might be better to order by number of messages associated to category or latest datetime for the messages
         of each category
        """
        list_categories_query = """
        MATCH (user:USER)-[:USES]->(category:CATEGORY)
        RETURN DISTINCT category.name as category_name
        ORDER by category_name
        """
        result = self.neo4jDriver.execute_read(list_categories_query)
        categories = [record["category_name"] for record in result]
        return categories

    def get_messages_by_category(self, category_name):
        """
        Retrieve all messages linked to a particular category.

        :param category_name: Name of the category node to investigate
        :return: all messages related to that category node
        """
        get_messages_query = """
        MATCH (user:USER)-[:USES]->(category:CATEGORY {name: $category_name})
            <-[:BELONGS_TO]-(user_prompt:USER_PROMPT)
        RETURN user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time
        ORDER by user_prompt.time
        """
        parameters = {"category_name": category_name}
        result = self.neo4jDriver.execute_write(get_messages_query, parameters)
        return result
