import logging
from datetime import datetime
from typing import List, Dict

import shortuuid as shortuuid

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data import CypherQueries
from Data.FileManagement import FileManagement
from Data.Neo4jDriver import Neo4jDriver
from Functionality.Organising import Organising
from Utilities import Constants


class NodeDatabaseManagement:
    def __init__(self):
        self.neo4jDriver = Neo4jDriver()
        self.executor = AiOrchestrator()

    def create_user_prompt_node(self, user_id: str, user_prompt: str, llm_response: str) -> str:
        """
        Saves a prompt - response pair as a USER_PROMPT in the neo4j database
        Categorising the prompt and staging any attached files under that category

        :param user_prompt: The given user prompt
        :param llm_response: The final response from the system
        :return: The category associated with the new user prompt node
        """
        time = int(datetime.now().timestamp())
        category_id = str(shortuuid.uuid())

        categories = self.list_categories()
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

        if category not in categories:
            logging.info(f"Creating new category [{category_id}]: {category}")
            parameters_for_new_category = {
                "category_name": category,
                "category_id": category_id,
            }
            self.neo4jDriver.execute_write(
                CypherQueries.CREATE_CATEGORY,
                parameters_for_new_category,
                "user_prompt_id"
            )

        parameters = {
            "prompt": user_prompt,
            "category_id": category_id,
            "response": llm_response,
            "time": time,
            "category": category
        }

        user_prompt_id = self.neo4jDriver.execute_write(
            CypherQueries.CREATE_USER_PROMPT_AND_CATEGORY_NODES,
            parameters,
            "user_prompt_id"
        )
        NodeDatabaseManagement.create_file_nodes_for_user_prompt(user_id, user_prompt_id, category)

        return category

    @staticmethod
    def create_file_nodes_for_user_prompt(user_id: str, user_prompt_id: str, category: str) -> None:
        file_names = FileManagement.list_staged_files(user_id)

        for file_name in file_names:
            NodeDatabaseManagement.create_file_node(user_prompt_id, category, file_name)

    @staticmethod
    def create_file_node(user_prompt_id: str, category: str, file_name: str) -> None:
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

        neo4j_driver = Neo4jDriver()
        parameters = {
            "category": category,
            "user_prompt_id": user_prompt_id,
            "name": file_name,
            "time": time,
            "summary": summary,
            "structure": "PROTOTYPING"
        }

        neo4j_driver.execute_write(CypherQueries.CREATE_FILE_NODE, parameters)

    # Messages

    def get_messages_by_category(self, category_name: str) -> List[Dict]:
        """
        Retrieve all messages linked to a particular category, newest first.

        :param category_name: Name of the category node to investigate
        :return: all messages related to that category node
        """
        parameters = {"category_name": category_name}

        records = self.neo4jDriver.execute_read(CypherQueries.GET_MESSAGES, parameters)
        messages_list = [
            {"id": record["id"],
             "prompt": record["prompt"],
             "response": record["response"],
             "time": record["time"]} for record in records]
        return messages_list

    def delete_message_by_id(self, message_id: int) -> None:
        """
        Deletes a specific message (isolated USER_PROMPT node) by its id.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        :param message_id: ID of the message to be deleted (Neo4j internal id or custom id)
        """
        message_id = int(message_id)
        parameters = {
            "message_id": message_id,
        }

        self.neo4jDriver.execute_delete(CypherQueries.DELETE_MESSAGE_AND_POSSIBLY_CATEGORY, parameters)

    # Categories

    def get_category_id(self, category_name: str) -> int:
        """
        Retrieve all files linked to a particular category, newest first.

        :param category_name: Name of the category node
        :return: the uuid of that category node
        """
        parameters = {"category_name": category_name}

        records = self.neo4jDriver.execute_read(CypherQueries.GET_CATEGORY_ID, parameters)
        category_id = records[0]["category_id"]
        logging.info(f"Category id for {category_name}: {category_id}")
        return category_id

    def list_categories(self) -> List[str]:
        """
        List all unique categories associated with the user

        ToDo: Might be better to order by number of messages associated to category or latest datetime for the messages
         of each category
        """
        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES)
        categories = [record["category_name"] for record in result]
        return categories

    def list_categories_with_files(self) -> List[str]:
        """
        List all unique categories associated with the user which have files attached
        """
        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES_WITH_FILES)
        categories = [record["category_name"] for record in result]
        return categories

    # Files

    def get_file_by_id(self, file_id: int):
        """
        Retrieve a file by its id, including the category its attached to
        ToDo: like most of these database calls we're going to have to ensure only the users files are
         accessed

        :param file_id: Neo4J id of the file
        :return: The singular file related to that id
        """
        parameters = {"file_id": file_id}
        records = self.neo4jDriver.execute_read(CypherQueries.GET_FILE_BY_ID, parameters)
        logging.info(f"File retrieved for file id [{file_id}]: {records}")

        if records:
            return records[0]
        return None

    def get_files_by_category(self, category_name: str) -> List[Dict]:
        """
        Retrieve all files linked to a particular category, newest first.

        :param category_name: Name of the category node to investigate
        :return: all messages related to that category node
        """
        logging.info(f"files: {category_name}")
        parameters = {"category_name": category_name}

        records = self.neo4jDriver.execute_read(CypherQueries.GET_FILES_FOR_CATEGORY, parameters)
        files_list = [
            {"id": record["id"],
             "category_id": record["category_id"],
             "name": record["name"],
             "summary": record["summary"],
             "structure": record["structure"],
             "time": record["time"]} for record in records]
        logging.info(f"Files retrieved: {files_list}")
        return files_list

    def delete_file_by_id(self, file_id: int) -> None:
        """
        Deletes a specific message (isolated USER_PROMPT node) by its id.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        :param file_id: ID of the file to be deleted (Neo4j internal id or custom id)
        """
        file_id = int(file_id)
        parameters = {
            "file_id": file_id,
        }

        self.neo4jDriver.execute_delete(CypherQueries.DELETE_FILE_BY_ID, parameters)
