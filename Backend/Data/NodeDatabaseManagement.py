import logging
import threading
import os
import shortuuid

from datetime import datetime
from typing import List, Dict, Optional, Any

from Constants import CypherQueries
from Constants.Exceptions import failed_to_create_user_topic
from Constants.Instructions import SUMMARISER_SYSTEM_INSTRUCTIONS
from Data.Configuration import Configuration
from Data.Neo4jDriver import Neo4jDriver
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context, get_message_context, get_earmarked_sum, set_earmarked_sum
from Utilities.Decorators import handle_errors, specify_functionality_context


class NodeDatabaseManagement:
    """
    Singleton class for managing interactions with the Neo4j database.
    ToDo: There is a bug where a user can login if they still have a access token even if their account no longer exists
     in the db

    It's tempting to split this class up, however neo4jDriver has a notable time to connect, however this may be
    negligible in a frequently used server
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Ensures a single instance of NodeDatabaseManagement."""
        if not cls._instance:
            with cls._lock:  # Ensure thread-safety during instance creation
                if not cls._instance:  # Double-check to avoid race conditions
                    cls._instance = super(NodeDatabaseManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialise the Neo4j driver instance."""
        if not hasattr(self, 'neo4jDriver'):
            self.neo4jDriver = Neo4jDriver()

    # User

    @handle_errors(debug_logging=True)
    def create_user(self, user_id: str, email: str, password_hash: str) -> bool:
        """Creates a new user in the database.

        :param user_id: Unique identifier for the user.
        :param email: User's email address.
        :param password_hash: Hashed password of the user.
        :return: True if the user is created successfully, False otherwise.
        """
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
            logging.info(f"User created successfully: {user_id}")
            return True

        return False

    @handle_errors()
    def user_exists(self, email: str) -> bool:
        """Check if a user with the given email exists.

        :param email: The email to check.
        :return: True if the user exists, False otherwise.
        """
        parameters = {"email": email}

        result = self.neo4jDriver.execute_read(
            CypherQueries.FIND_USER_BY_EMAIL,
            parameters
        )
        return bool(result)

    @handle_errors()
    def mark_user_email_verified(self, email: str) -> bool:
        """When email verification has completed successfully we mark it against the USER node

        :param email: The email to check.
        :return: True if the user exists, False otherwise.
        """
        parameters = {"email": email}

        result = self.neo4jDriver.execute_write(
            CypherQueries.MARK_VERIFIED,
            parameters,
            'verified_status'
        )

        return result

    @handle_errors()
    def find_user_by_email(self, email: str) -> Optional[str]:
        """Return the user id for a given email address.

        :param email: Email to search for.
        :return: The user_id if found, None otherwise.
        """
        parameters = {"email": email}

        records = self.neo4jDriver.execute_read(
            CypherQueries.FIND_USER_BY_EMAIL,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database Catastrophe: Shared email address [{email}]!")
            raise ValueError(f"Multiple users found for email: {email}")

        if records:
            return records[0]["user_id"]

        return None

    @handle_errors()
    def get_user_password_hash(self, user_id: str) -> Optional[str]:
        """Return the hashed password for a given user ID.

        :param user_id: The unique identifier for the user.
        :return: The hashed password if found, None otherwise.
        """
        parameters = {"user_id": user_id}

        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_USER_PASSWORD_HASH,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database error: Multiple password hashes found for user [{user_id}]!")

        return records[0]["password_hash"] if records else None

    # Messages

    @handle_errors()
    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a message by its id.

        :param message_id: ID of the message.
        :return: A dictionary with message details if found, None otherwise.
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": message_id,
        }

        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_MESSAGE,
            parameters
        )

        if records:
            record = records[0]
            return {
                "id": record["id"],
                "prompt": record["prompt"],
                "response": record["response"],
                "time": record["time"]
            }

        return None

    @handle_errors()
    def create_user_prompt_node(self, category: str) -> str:
        """
        Creates a placeholder USER_PROMPT node in the neo4j database, to be populated and connected to a
        CATEGORY and thereby to a USER later in the request.

        :param category: Category the new user prompt will belong to
        :return: The user_prompt_id associated with the new user prompt node.
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": get_message_context(),
            "category": category
        }

        user_prompt_id = self.neo4jDriver.execute_write(
            CypherQueries.CREATE_USER_PROMPT_NODE,
            parameters,
            "user_prompt_id"
        )

        logging.info(f"User prompt node created with ID: {user_prompt_id} for category: {category}")
        return user_prompt_id

    @handle_errors()
    def populate_user_prompt_node(self, category: str, user_prompt: str, llm_response: str) -> str | None:
        """
        Populates the data for a USER_PROMPT prompt - response pairing, in the neo4j database.
        Additionally connecting it to a CATEGORY and therefore made accessible to the USER.

        Returns None if it fails to find the USER_PROMPT to populate

        :param category: Category of the user prompt.
        :param user_prompt: The user prompt content.
        :param llm_response: The response generated by the language model.
        :return: The category associated with the user prompt node.
        """
        time = int(datetime.now().timestamp())
        logging.info(
            f"Attempting to populate USER_PROMPT: user_id{get_user_context()}, message_id: {get_message_context()}, "
            f"category: {category}")

        parameters = {
            "user_id": get_user_context(),
            "message_id": get_message_context(),
            "prompt": user_prompt,
            "response": llm_response,
            "time": time,
            "category": category
        }

        user_prompt_id = self.neo4jDriver.execute_write(
            CypherQueries.POPULATE_USER_PROMPT_NODE,
            parameters,
            "user_prompt_id"
        )

        logging.info(f"User prompt node populated with ID: {user_prompt_id}")
        return user_prompt_id

    @handle_errors()
    def get_messages_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Retrieve messages linked to a specific category.

        :param category_name: The category to retrieve messages for.
        :return: A list of messages related to that category.
        """
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

        records = self.neo4jDriver.execute_read(CypherQueries.GET_MESSAGES, parameters)
        return [
            {"id": record["id"],
             "prompt": record["prompt"],
             "response": record["response"],
             "cost": record.get("cost", 0),
             "time": record["time"]} for record in records
        ]

    @handle_errors()
    def delete_message_by_id(self, message_id: str) -> None:
        """Deletes a message by its ID.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        :param message_id: ID of the message to delete.
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": message_id,
        }

        self.neo4jDriver.execute_delete(CypherQueries.DELETE_MESSAGE_AND_POSSIBLY_CATEGORY, parameters)
        logging.info(f"User prompt node {message_id} deleted")

    # Categories

    @handle_errors()
    def create_category(
        self,
        category_id: str,
        category_name: str,
        category_description: str,
        colour: str = "#111111"
    ) -> None:
        """Creates a new category in the database.

        :param category_id: The id of the new category node
        :param category_name: The name of the new category.
        :param category_description: A concise one sentence description of the new category
        :param colour: the HEX colour assigned to the category
        """
        logging.info(f"Creating new category [{category_id}]: {category_name} - {category_description}")

        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name.lower(),
            "category_description": category_description,
            "category_id": category_id,
            "colour": colour
        }

        self.neo4jDriver.execute_write(
            CypherQueries.CREATE_CATEGORY,
            parameters
        )

    @handle_errors()
    def create_category_and_user_prompt(
        self,
        category_id: str,
        category_name: str,
        category_description: str,
        colour: str = "#111111",
    ) -> None:
        """
        Creates a new category in the database and user prompt when the conditions have been established that the prompt
        doesn't belong to an existing category.

        Required as certain models (Gemini) are so fast they can execute before the neo4j has actually finalised a new
        category transaction record and can return said category later in the request.

        :param category_id: The id of the new category node
        :param category_name: The name of the new category.
        :param category_description: A concise one sentence description of the new category
        :param colour: the HEX colour assigned to the category
        """

        logging.info(f"Creating new category [{category_id}]: {category_name} - {category_description}")

        parameters = {
            "user_id": get_user_context(),
            "message_id": get_message_context(),
            "category_name": category_name.lower(),
            "category_description": category_description,
            "category_id": category_id,
            "colour": colour
        }

        self.neo4jDriver.execute_write(
            CypherQueries.CREATE_USER_PROMPT_BLANK_AND_CATEGORY,
            parameters
        )

    @handle_errors()
    def get_category_id(self, category_name: str) -> Optional[str]:
        """Retrieve the ID of a category by its name.

        :param category_name: Name of the category.
        :return: The ID of the category if found, None otherwise.
        """
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_CATEGORY_ID,
            parameters)
        category_id = records[0]["category_id"]

        logging.info(f"Category ID for {category_name}: {category_id}")
        return category_id

    @handle_errors()
    def list_category_names(self) -> List[Dict[str, str]]:
        """Lists the names of categories

        :return: A list of category names.
        """
        parameters = {
            "user_id": get_user_context()
        }

        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES, parameters)
        return [record["category_name"] for record in result]

    @handle_errors()
    def list_categories(self) -> List[Dict[str, str]]:
        """
        Lists all unique categories associated with the user and their associated data.
        e.g. Assigned colour

        :return: A list of category and associated data.
        """
        parameters = {"user_id": get_user_context()}

        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES_BY_LATEST_MESSAGE, parameters)
        categories = [{"name": record["category_name"], "description": record.get("description"), "colour": record["colour"]} for record in result]

        return categories

    def list_categories_with_files(self) -> List[Dict[str, str]]:
        """
        List all unique categories associated with the user which have files attached
        """
        parameters = {"user_id": get_user_context()}

        result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES_WITH_FILES_BY_LATEST_FILE, parameters)
        categories = [{"name": record["category_name"], "colour": record["colour"]} for record in result]

        return categories

    # Files

    @handle_errors()
    def create_file_node(self, category_id: str, file_path: str) -> str:
        """Creates a file node in the database representing the file content.

        :param category_id: Category id of the file.
        :param file_path: Path to the file.
        :returns: The UUID of the new file node
        """
        file_uuid = str(shortuuid.uuid())
        time = int(datetime.now().timestamp())
        file_name = os.path.basename(file_path)
        user_prompt_id = get_user_context()

        summary = self.summarise_file(file_path)

        parameters = {
            "file_id": file_uuid,
            "user_id": get_user_context(),
            "category_id": category_id,
            "user_prompt_id": user_prompt_id,
            "name": file_name,
            "time": time,
            "summary": summary,
            "structure": "PROTOTYPING"
        }

        logging.info(f"Creating file node: {file_path} against prompt [{user_prompt_id}]\nSummary: {summary}")
        self.neo4jDriver.execute_write(
            CypherQueries.CREATE_FILE_NODE,
            parameters
        )

        return file_uuid

    @staticmethod
    @specify_functionality_context("summarise_files")
    def summarise_file(file_path: str):
        """
        ToDo: May need to refactor @specify_functionality_context because it can't be locally imported, NodeDB should be
         low on the dependency tree but it occasionally needs to run methods like this from classes which themselves
         must use NodeDB
        """
        config = Configuration.load_config()

        if config.get('files', {}).get('summarise_files', False):
            content = StorageMethodology.select().read_file(file_path)

            from AiOrchestration.AiOrchestrator import AiOrchestrator
            summary = AiOrchestrator().execute(
                [config.get("system_messages", {}).get(
                    'file_summarisation_message',
                    SUMMARISER_SYSTEM_INSTRUCTIONS
                )],
                [content]
            )
        else:
            summary = ""

        return summary

    @handle_errors()
    def get_file_by_id(self, file_id: int):
        """
        Retrieve a file by its id, including the category its attached to
        ToDo: like most of these database calls we're going to have to ensure only the users files are
         accessed.

        :param file_id: ID of the file.
        :return: The file record if found, None otherwise.
        """
        parameters = {
            "user_id": get_user_context(),
            "file_id": file_id
        }

        records = self.neo4jDriver.execute_read(CypherQueries.GET_FILE_BY_ID, parameters)
        if not records:
            return None

        record = records[0]

        return {
            "id": record["id"],
            "category_id": record["category"],
            "name": record["name"],
            "summary": record["summary"],
            "structure": record["structure"],
            "time": record["time"]
        }

    @handle_errors()
    def get_files_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Retrieve all files associated with a specified category.

        :param category_name: Name of the category.
        :return: A list of files related to that category.
        """
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

        records = self.neo4jDriver.execute_read(CypherQueries.GET_FILES_FOR_CATEGORY, parameters)
        return [
            {
                "id": record["id"],
                "category_id": record["category_id"],
                "name": record["name"],
                "summary": record["summary"],
                "structure": record["structure"],
                "time": record["time"]
            } for record in records
        ]

    @handle_errors()
    def delete_file_by_id(self, file_id: str) -> None:
        """
        Deletes a specific message (isolated USER_PROMPT node) by its Neo4j internal id.
        If the CATEGORY the message is associated with has no more messages, it deletes the CATEGORY node as well.

        ToDo: Eventually needs to move to deleting by assigned id before accessing neo4j internal id's is phased out

        :param file_id: ID of the file to be deleted.
        """
        parameters = {
            "user_id": get_user_context(),
            "file_id": str(file_id),
        }

        self.neo4jDriver.execute_delete(CypherQueries.DELETE_FILE_BY_ID, parameters)
        logging.info(f"File with ID {file_id} deleted")

    # User Topics

    def create_user_topic_nodes(self, terms: List[Dict[str, str]]) -> None:
        """Creates user topic nodes in the database.

        :param terms: List of terms to create user topics for.
        """
        logging.info(f"Noted the following user topics: {terms}")

        for term in terms:
            parameters = {
                "user_id": get_user_context(),
                "node_name": term.get('node').lower(),
                "content": term.get('content')
            }
            try:
                self.neo4jDriver.execute_write(
                    CypherQueries.format_create_user_topic_query(term.get('parameter')),
                    parameters
                )
            except Exception:
                logging.exception(failed_to_create_user_topic(str(term)))

    @handle_errors()
    def search_for_user_topic_content(self, term: str, synonyms: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Searches for user topic content in the database.

        :param term: The term to search for.
        :param synonyms: Optional list of synonyms to consider for the search.
        :return: The content associated with the term if found, None otherwise.
        """
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
                logging.info(f"Extracted content for {term}: {node_content}")
                return node_content

    @handle_errors()
    def list_user_topics(self) -> Optional[List[str]]:
        """Lists all user topics.

        :return: A list of user topic names if found, None otherwise.
        """
        parameters = {"user_id": get_user_context()}

        records = self.neo4jDriver.execute_read(
            CypherQueries.SEARCH_FOR_ALL_USER_TOPICS,
            parameters
        )
        if records:
            names = [record['name'] for record in records]
            return names

    # Pricing

    @handle_errors()
    def get_user_balance(self) -> Optional[float]:
        """Returns the current user balance.

        :return: The user balance if found, None otherwise.
        """
        parameters = {"user_id": get_user_context()}

        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_USER_BALANCE,
            parameters
        )
        if len(records) > 1:
            logging.error(f"Database Catastrophe: Multiple records found for user ID: {get_user_context()}!")
        return records[0]["balance"]

    @handle_errors()
    def get_user_earmarked_balance(self) -> Optional[float]:
        """Returns the amount earmarked for currently occurring transactions

        :return: The user earmarked sum if found, None otherwise.
        """
        parameters = {"user_id": get_user_context()}

        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_EARMARKED_SUM,
            parameters
        )
        if len(records) > 1:
            logging.error(f"Database Catastrophe: Multiple records found for user ID: {get_user_context()}!")
        return records[0]["earmarked_sum"]

    @handle_errors()
    def earmark_from_user_balance(self, earmarked_sum: float):
        """
        Reserves an estimated amount of currency in advance of a transaction after the transaction occurs this earmarked
        amount is returned to the users balance and the real fee deduced.
        """
        if earmarked_sum <= 0:
            logging.error("Earmarking amount must be positive.")
            return

        parameters = {
            "user_id": get_user_context(),
            "amount": earmarked_sum
        }

        earmarked_total = self.neo4jDriver.execute_write(
            CypherQueries.EARMARK_AGAINST_USER_BALANCE,
            parameters,
            'total_earmarked'
        )
        set_earmarked_sum(earmarked_sum)

        logging.info(
            f"Earmarked from user balance for ongoing AI request: {earmarked_sum}"
            f" - total currently earmarked: {earmarked_total}"
        )

    @handle_errors()
    def deduct_from_user_balance(self, amount: float) -> None:
        """Deducts a specific amount from the user's balance.

        Making it *very* obvious

        :param amount: The amount to deduct (should be a positive value).
        """
        if amount <= 0:
            logging.error("Deduction amount must be positive.")
            return

        self.update_user_balance(-amount)

    @handle_errors()
    def update_user_balance(self, amount: float) -> None:
        """Updates the user's balance by the specified amount.

        :param amount: positive for an amount to add to the users balance. DON'T GET THE F###ING SIGN WRONG
        """
        earmarked_sum = get_earmarked_sum()
        parameters = {
            "user_id": get_user_context(),
            "amount": amount,
            "earmarkedAmount": earmarked_sum
        }

        self.neo4jDriver.execute_write(
            CypherQueries.UPDATE_USER_BALANCE,
            parameters
        )
        logging.info(f"User balance updated by: {amount} (earmarked value: {earmarked_sum}")

    # Pricing - Gemini management

    @handle_errors()
    def get_system_gemini_balance(self) -> Optional[float]:
        """Returns the SYSTEM gemini account balance, when this hits 0 gemini calls are blocked

        :return: The system balance if found, None otherwise.
        """

        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_SYSTEM_GEMINI_BALANCE
        )
        if len(records) > 1:
            logging.error(f"Database Catastrophe: Multiple SYSTEM records found!!")
        return records[0]["gemini_balance"]

    @handle_errors()
    def deduct_from_system_gemini_balance(self, amount: float) -> None:
        """Deducts a specific amount from the systems gemini balance total

        :param amount: The amount to deduct (should be a positive value).
        """
        if amount <= 0:
            logging.error("Deduction amount must be positive.")
            return

        self.update_system_gemini_balance(-amount)

    @handle_errors()
    def update_system_gemini_balance(self, amount: float) -> None:
        """Updates the user's balance by the specified amount.

        :param amount: positive for an amount to add to the users balance.
        """
        parameters = {
            "amount": amount
        }

        self.neo4jDriver.execute_write(
            CypherQueries.UPDATE_SYSTEM_GEMINI_BALANCE,
            parameters
        )
        logging.info(f"System gemini balance updated by: {amount}")

    @handle_errors()
    def expense_node(self, node_id: str, amount: float) -> None:
        """Attaches a cost information to a give node

        :param node_id: the node to expense
        :param amount: positive to assign a cost to a given functionality or message. eh whatever bro
        """
        parameters = {
            "node_id": node_id,
            "amount": amount
        }

        status = self.neo4jDriver.execute_write(
            CypherQueries.EXPENSE_NODE,
            parameters
        )
        logging.info(f"Node with UUID [{node_id}] updated by [{amount}] - {status}")

    @handle_errors()
    def expense_functionality(self, functionality: str, amount: float) -> None:
        """Attaches a cost information to a give node

        :param functionality: the functionality usage estimate to update
        :param amount: positive to assign a cost to a given functionality or message. eh whatever bro
        """
        parameters = {
            "user_id": get_user_context(),
            "functionality": functionality + "_cost",
            "amount": amount
        }

        new_total = self.neo4jDriver.execute_write(
            CypherQueries.EXPENSE_FUNCTIONALITY,
            parameters
        )
        logging.info(f"User functionality {functionality} updated by [{amount}] - Total: {new_total}")

    @handle_errors()
    def get_user_information(self, parameters):
        """
        Fetch user information based on a list of parameters.

        :param parameters: List of parameter names to retrieve.
        :return: Dictionary of user information.
        """
        query = CypherQueries.fetch_user_params_query(get_user_context(), parameters)

        records = self.neo4jDriver.execute_read(
            query
        )
        if not records:
            return None

        return records[0].data()

    # Promotions

    def check_new_user_promotion_active(self):
        records = self.neo4jDriver.execute_read(
            CypherQueries.NEW_USER_PROMOTIONS_REMAINING
        )

        remaining_promotions = records[0].get("new_user_promotions_remaining", 0)

        if type(remaining_promotions) == int and remaining_promotions > 0:
            return True

        return False

    def add_new_user_promotion(self, email: str) -> int | None:
        """
        Will attempt to add a new user promotion against the account with the specified email
        # ToDo: would be nice to see user_balance information too but would require re-write of neo4jdriver's
        execute_write method

        :param email:
        :return:
        """
        parameters = {
            "email": email,
        }

        remaining_promotions = self.neo4jDriver.execute_write(
            CypherQueries.APPLY_NEW_USER_PROMOTION,
            parameters,
            'new_user_promotions_remaining'
        )
        if remaining_promotions is None:
            logging.warning(f"New user promotion could not be applied for user [{email}].  No promotions remaining.")
            return None

        logging.info(
            f"New user promotion applied, user [{email}], remaining promotions: {remaining_promotions}")
        return remaining_promotions
