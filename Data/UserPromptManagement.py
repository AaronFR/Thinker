import logging
from datetime import datetime

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.CategoryManagement import CategoryManagement
from Data.FileManagement import FileManagement
from Data.Neo4jDriver import Neo4jDriver
from Functionality.Organising import Organising
from Utilities import Constants


class UserPromptManagement:
    def __init__(self):
        self.neo4jDriver = Neo4jDriver()
        self.executor = AiOrchestrator()

    def create_user_prompt_node(self, user_prompt, llm_response):
        """
        Saves a prompt - response pair as a USER_PROMPT in the neo4j database
        Categorising the prompt and staging any attached files under that category

        :param user_prompt: The given user prompt
        :param llm_response: The final response from the system
        :return:
        """
        time = int(datetime.now().timestamp())

        categories = self.list_user_categories()
        categorisation_input = "<user prompt>" + user_prompt + "</user prompt>\n" + \
                               "<response>" + llm_response + "</response>"
        category_data = self.executor.execute_function(
            ["Given the following prompt-response pair, categorize the data with the most suitable single-word answer."
             "The categories provided are a backup option, to be used only if they are the most fitting: " + str(
                categories) + "."
             "If none of the categories are appropriate, feel free to generate a more suitable term."],
            [categorisation_input],
            Constants.DETERMINE_CATEGORY_FUNCTION_SCHEMA
        )
        logging.info("category_data:", category_data)
        category = category_data["category"]

        create_user_prompt_query = """
        MERGE (user:USER)
        MERGE (category:CATEGORY {name: $category})
        CREATE (user_prompt:USER_PROMPT {prompt: $prompt, response: $response, time: $time})
        MERGE (user)-[:USES]->(category)
        MERGE (user_prompt)-[:BELONGS_TO]->(category)
        RETURN id(user_prompt) AS user_prompt_id
        """
        parameters = {
            "prompt": user_prompt,
            "response": llm_response,
            "time": time,
            "category": category
        }

        user_prompt_id = self.neo4jDriver.execute_write(create_user_prompt_query, parameters, "user_prompt_id")
        UserPromptManagement.create_file_nodes_for_user_prompt(user_prompt_id, category)

        categoryManagement = CategoryManagement()
        categoryManagement.stage_files(user_prompt, category)

        return user_prompt_id

    @staticmethod
    def create_file_nodes_for_user_prompt(user_prompt_id: str, category: str):
        file_names = FileManagement.list_file_names()

        for file_name in file_names:
            UserPromptManagement.create_file_node(user_prompt_id, category, file_name)

    @staticmethod
    def create_file_node(user_prompt_id: str, category: str, file_name: str):
        """
        Saves a prompt - response pair as a USER_PROMPT in the neo4j database
        Categorising the prompt and staging any attached files under that category

        :param user_prompt_id: create the file node attached to the following message
        :param category: The name of the category the file belongs to
        :file_name: the name of the file, including extension
        """
        time = int(datetime.now().timestamp())
        content = FileManagement.read_file(file_name)
        summary = Organising.summarise_content(content)

        neo4jDriver = Neo4jDriver()
        create_file_query = """
            MERGE (user:USER)
            MERGE (category:CATEGORY {name: $category})
            WITH user, category
            MATCH (user_prompt:USER_PROMPT)
            WHERE id(user_prompt) = $user_prompt_id
            CREATE (file:FILE {name: $name, time: $time, summary: $summary, structure: $structure})
            MERGE (file)-[:ORIGINATES_FROM]->(user_prompt)
            MERGE (file)-[:BELONGS_TO]->(category)
            RETURN file
            """
        parameters = {
            "category": category,
            "user_prompt_id": user_prompt_id,
            "name": file_name,
            "time": time,
            "summary": summary,
            "structure": "PROTOTYPING"
        }

        result = neo4jDriver.execute_write(create_file_query, parameters)
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
        Retrieve all messages linked to a particular category, newest first.

        :param category_name: Name of the category node to investigate
        :return: all messages related to that category node
        """
        get_messages_query = """
        MATCH (user:USER)-[:USES]->(category:CATEGORY {name: $category_name})
            <-[:BELONGS_TO]-(user_prompt:USER_PROMPT)
        RETURN id(user_prompt) AS id, user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time
        ORDER by user_prompt.time DESC
        """
        parameters = {"category_name": category_name}
        result = self.neo4jDriver.execute_read(get_messages_query, parameters)
        return result

    def get_files_by_category(self, category_name):
        """
        Retrieve all files linked to a particular category, newest first.

        :param category_name: Name of the category node to investigate
        :return: all messages related to that category node
        """
        logging.info(f"files: {category_name}")
        get_messages_query = """
        MATCH (user:USER)-[:USES]->(category:CATEGORY {name: $category_name})
            <-[:BELONGS_TO]-(file:FILE)
        RETURN id(file) AS id, id(category) AS category_id, file.name AS name, file.summary AS summary, file.structure AS structure, file.time AS time
        ORDER by file.time DESC
        """
        parameters = {"category_name": category_name}
        result = self.neo4jDriver.execute_read(get_messages_query, parameters)
        logging.info(f"Files retrieved: {result}")
        return result

    def get_file_by_id(self, file_id):
        """
        Retrieve a file by its id, including the category its attached to
        ToDo: like most of these database calls we're going to have to ensure only the users files are
         accessed

        :param file_id: Neo4J id of the file
        :return: all messages related to that category node
        """
        get_messages_query = """
        MATCH (category:CATEGORY)--(file:FILE)
        WHERE id(file) = $file_id
        RETURN id(file) AS id, id(category) AS category, file.name AS name, file.summary AS summary, file.structure AS structure, file.time AS time
        ORDER by file.time DESC
        """
        parameters = {"file_id": file_id}
        result = self.neo4jDriver.execute_read(get_messages_query, parameters)
        logging.info(f"File retrieved: {result}")
        return result

    def delete_message_by_id(self, message_id: int):
        """
        Deletes a specific message (isolated USER_PROMPT node) by its id.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        :param message_id: ID of the message to be deleted (Neo4j internal id or custom id)
        """
        message_id = int(message_id)

        delete_query = """
        MATCH (message:USER_PROMPT)-[:BELONGS_TO]->(category:CATEGORY)
        WHERE id(message) = $message_id
        DETACH DELETE message
        WITH category
        OPTIONAL MATCH (category)<-[:BELONGS_TO]-(remaining_messages:USER_PROMPT)
        WITH category, count(remaining_messages) AS remaining_count
        WHERE remaining_count = 0
        DETACH DELETE category
        """
        parameters = {
            "message_id": message_id,
        }

        result = self.neo4jDriver.execute_delete(delete_query, parameters)
        return result

    def delete_file_by_id(self, file_id: int):
        """
        Deletes a specific message (isolated USER_PROMPT node) by its id.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        :param file_id: ID of the file to be deleted (Neo4j internal id or custom id)
        """
        file_id = int(file_id)

        delete_query = """
        MATCH (file:FILE)-[:BELONGS_TO]->(category:CATEGORY)
        WHERE id(file) = $file_id
        DETACH DELETE file
        """
        parameters = {
            "file_id": file_id,
        }

        result = self.neo4jDriver.execute_delete(delete_query, parameters)
        return result
