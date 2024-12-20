import logging
import threading
import os
import shortuuid

from datetime import datetime
from typing import List, Dict

from Data import CypherQueries
from Data.Neo4jDriver import Neo4jDriver
from Data.Files.StorageMethodology import StorageMethodology
from Personas.PersonaSpecification import PersonaConstants
from Utilities.Contexts import get_user_context

from Utilities.Contexts import get_message_context


class NodeDatabaseManagement:
    """
    Singleton class for managing interactions with the Neo4j database.
    ToDo: each method should try catch for errors
    ToDo: There is a bug where a user can login if they still have a access token even if their account no longer exists
     in the db

    It's tempting to split this class up, however neo4jDriver has a notable time to connect, however this may be
    negligible in a frequently used server
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # Ensure thread-safety during instance creation
                if not cls._instance:  # Double-check to avoid race conditions
                    cls._instance = super(NodeDatabaseManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "neo4jDriver"):  # Prevent reinitialization
            self.neo4jDriver = Neo4jDriver()

    # User

    def create_user(self, user_id, email, password_hash):
        parameters = {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash
        }
        returned_user_id = self.neo4jDriver.execute_write(
            CypherQueries.CREATE_USER,
            parameters,
            "user.id"
        )

        if returned_user_id:
            StorageMethodology.select().add_new_user_file_folder(returned_user_id)
            return True
        return False

    def user_exists(self, email):
        """
        Check if a user node with the given email already exists.
        """
        parameters = {
            "email": email
        }
        result = self.neo4jDriver.execute_read(
            CypherQueries.FIND_USER_BY_EMAIL,
            parameters
        )
        return bool(result)  # Will return False if no user is found

    def find_user_by_email(self, email):
        """
        Return the user id for a given (unique) email address

        :param email: The email to search for in the system
        :return: The file friendly uuid associated with the email address
        """
        parameters = {
            "email": email
        }
        records = self.neo4jDriver.execute_read(
            CypherQueries.FIND_USER_BY_EMAIL,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database Catastrophe: Shared email address [{email}]!")

        return records[0]["user_id"]

    def get_user_password_hash(self, user_id):
        """
        Returns the hashed password for a given user id

        :param user_id: The uuid associated with the user
        :return: Their hashed password
        """
        parameters = {
            "user_id": user_id
        }
        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_USER_PASSWORD_HASH,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database Catastrophe: These UUID's aren't very unique! [{user_id}]!")
            # for the record I'm saying this would be my fault not a uuid generators.

        return records[0]["password_hash"]

    # Messages

    def get_message_by_id(self, message_id) -> Dict[str, str]:
        """
        Retrieves a message by its uuid

        :param message_id: The uuid of the message
        :return: The details of the message node
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": message_id,
        }
        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_MESSAGE,
            parameters
        )

        record = records[0]
        message = {
            "id": record["id"],
            "prompt": record["prompt"],
            "response": record["response"],
            "time": record["time"]
        }

        return message

    def create_user_prompt_node(self, category: str, user_prompt: str, llm_response: str) -> str:
        """
        Saves a prompt - response pair as a USER_PROMPT in the neo4j database
        Categorising the prompt and staging any attached files under that category

        :param user_prompt: The given user prompt
        :param llm_response: The final response from the system
        :return: The category associated with the new user prompt node
        """
        time = int(datetime.now().timestamp())

        parameters = {
            "user_id": get_user_context(),
            "message_id": get_message_context(),
            "prompt": user_prompt,
            "response": llm_response,
            "time": time,
            "category": category
        }
        user_prompt_id = self.neo4jDriver.execute_write(
            CypherQueries.CREATE_USER_PROMPT_NODES,
            parameters,
            "user_prompt_id"
        )

        self.create_file_nodes_for_user_prompt(user_prompt_id, category)

        return category

    def get_messages_by_category(self, category_name: str) -> List[Dict]:
        """
        Retrieve all messages linked to a particular category, newest first.

        :param category_name: Name of the category node to investigate
        :return: all messages related to that category node
        """
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

        records = self.neo4jDriver.execute_read(CypherQueries.GET_MESSAGES, parameters)
        messages_list = [
            {"id": record["id"],
             "prompt": record["prompt"],
             "response": record["response"],
             "time": record["time"]} for record in records]
        return messages_list

    def delete_message_by_id(self, message_id: str) -> None:
        """
        Deletes a specific message (isolated USER_PROMPT node) by its id.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        :param message_id: UUID of the message to be deleted
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": message_id,
        }

        self.neo4jDriver.execute_delete(CypherQueries.DELETE_MESSAGE_AND_POSSIBLY_CATEGORY, parameters)
        logging.info(f"User prompt node {message_id} deleted")

    # Categories

    def create_category(self, category_name: str):
        category_id = str(shortuuid.uuid())
        logging.info(f"Creating new category [{category_id}]: {category_name}")

        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name.lower(),
            "category_id": category_id
        }
        self.neo4jDriver.execute_write(
            CypherQueries.CREATE_CATEGORY,
            parameters
        )

    def get_category_id(self, category_name: str) -> str:
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
        parameters = {
            "user_id": get_user_context()
        }
        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES, parameters)
        categories = [record["category_name"] for record in result]
        return categories

    def list_categories_with_files(self) -> List[str]:
        """
        List all unique categories associated with the user which have files attached
        """
        parameters = {
            "user_id": get_user_context()
        }
        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES_WITH_FILES, parameters)
        categories = [record["category_name"] for record in result]
        return categories

    # Files

    def create_file_nodes_for_user_prompt(self, user_prompt_id: str, category: str) -> None:
        file_names = StorageMethodology.select().list_staged_files()

        for file_name in file_names:
            self.create_file_node(user_prompt_id, category, file_name)

    def create_file_node(self, user_prompt_id: str, category: str, file_path: str) -> None:
        """
        Saves a file node representing the files content, its category and its version number

        ToDo: the usage of file_name/file_path/full_path is very convoluted and needs to be made systematic

        :param user_prompt_id: create the file node attached to the following message
        :param category: The name of the category the file belongs to
        :param file_path: the name of the file, including extension
        """
        try:
            time = int(datetime.now().timestamp())
            # category_id = self.get_category_id(category)
            file_name = os.path.basename(file_path)

            content = StorageMethodology.select().read_file(file_path)
            from AiOrchestration.AiOrchestrator import AiOrchestrator
            executor = AiOrchestrator()
            #ToDo: Summarises previous content if it exists when writing files
            summary = executor.execute(
                [PersonaConstants.SUMMARISER_SYSTEM_INSTRUCTIONS],
                [content]
            )

            parameters = {
                "user_id": get_user_context(),
                "category": category,
                "user_prompt_id": user_prompt_id,
                "name": file_name,
                "time": time,
                "summary": summary,
                "structure": "PROTOTYPING"
            }

            logging.info(f"Creating file node: {category}/{file_name} against prompt [{user_prompt_id}]\nsummary: {summary}")
            self.neo4jDriver.execute_write(CypherQueries.CREATE_FILE_NODE, parameters)
        except Exception:
            logging.exception("Failed to save file node")

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
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

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
            "user_id": get_user_context(),
            "file_id": file_id,
        }

        self.neo4jDriver.execute_delete(CypherQueries.DELETE_FILE_BY_ID, parameters)

    # User Topics

    def create_user_topic_nodes(self, terms):
        logging.info(f"Noted the following user topics : {terms}")

        for term in terms:
            parameters = {
                "user_id": get_user_context(),
                "node_name": term.get('node').lower(),
                "content": term.get('content')
            }
            self.neo4jDriver.execute_write(
                CypherQueries.format_create_user_topic_query(term.get('parameter')),
                parameters
            )

    def search_for_user_topic_content(self, term, synonyms=None):
        logging.info(f"Attempting search for the following term: {term}")
        parameters = {
            "user_id": get_user_context(),
            "node_name": term
        }
        records = self.neo4jDriver.execute_read(
            CypherQueries.SEARCH_FOR_USER_TOPIC,
            parameters
        )
        if records:
            record = records[0]
            if record:
                node_content = record["all_properties"]

                logging.info(f"Extracted content for {term} : {node_content}")
                return node_content

        return None

    def list_user_topics(self):
        """
        Returns the usernames of the USER TOPICs arranged newest first

        :return:
        """
        parameters = {
            "user_id": get_user_context()
        }
        records = self.neo4jDriver.execute_read(
            CypherQueries.SEARCH_FOR_ALL_USER_TOPICS,
            parameters
        )
        if records:
            names = [record['name'] for record in records]
            return names

        return None

    # Pricing

    def get_user_balance(self):
        """
        Returns the hashed password for a given user id

        :return: Their hashed password
        """
        parameters = {
            "user_id": get_user_context()
        }
        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_USER_BALANCE,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database Catastrophe: Multiple users for a user id! [{get_user_context()}]!")

        return records[0]["balance"]

    def deduct_from_user_balance(self, sum: float):
        """
        Making it *very* obvious

        :param sum: positive amount to deduct from the balance
        """
        self.update_user_balance(-sum)

    def update_user_balance(self, sum: float):
        """
        Returns the hashed password for a given user id

        :param sum: positive for an amount to add to the users balance. DON'T GET THE F###ING SIGN WRONG
        :return: Their hashed password
        """
        parameters = {
            "user_id": get_user_context(),
            "sum": sum
        }
        self.neo4jDriver.execute_write(
            CypherQueries.UPDATE_USER_BALANCE,
            parameters
        )

    def create_receipt(self, input_costs, output_costs, mode):
        """
        Creates a receipt representing a transaction cost to the user

        :return: Their hashed password
        """
        logging.info(f"Logging receipt: {input_costs}, {output_costs}, {mode}, {get_user_context()}, {get_message_context()}")
        parameters = {
            "user_id": get_user_context(),
            "message_id": get_message_context(),
            "input_costs": input_costs,
            "output_costs": output_costs,
            "mode": mode
        }
        results = self.neo4jDriver.execute_write(
            CypherQueries.CREATE_RECEIPT,
            parameters
        )
