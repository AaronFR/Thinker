# Outputs for Altered Enhanced System Message

All of my comments will be prefaced  # REVIEW: 

## WikipediaApi.py
```python
# REVIEW: By default llm's appear to want no newlines in imports, don't know why, don't like it myself.
import logging
import os
import re
import requests
import wikipediaapi
from typing import Dict, Optional, List
from Data.Files.FileManagement import FileManagement
from Utilities.Decorators import handle_errors

# Constants
DATA_PATH = os.path.join(os.path.dirname(__file__), '../../UserData/DataStores')
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
WIKI_PREFIX = 'ThinkerBot (https://github.com/AaronFR/Thinker)'

# REVIEW: all methods are spaced apart by 1 line not 2 which would be correct for a methods outside a class
def _section_to_dict(section) -> Dict[str, object]:
    """
    Recursively converts a Wikipedia section and its subsections to a dictionary.

    :param section: The section from a Wikipedia page.
    :return: A dictionary representation of the section and its subsections.
    """
    section_dict = {'content': section.text}
    if section.sections:
        section_dict['subsections'] = {
            subsection.title: _section_to_dict(subsection) for subsection in section.sections
        }
    return section_dict

def search_wikipedia_api(term: str, file_name: str = "Encyclopedia") -> None:
    """
    Fetches a Wikipedia page for the given term and caches the content in a local Encyclopedia cache.

    If the page content already exists, it skips the fetch and logs a message.

    :param term: The title of the Wikipedia page to fetch.
    :param file_name: The base name (without extension) for the output YAML file.
    """
    yaml_filename = f"{file_name}.yaml"
    yaml_path = os.path.join(DATA_PATH, yaml_filename)

    existing_data = FileManagement.load_yaml(yaml_path)
    if term in existing_data:
        logging.info(f"Data for '{term}' is already present in {yaml_filename}. Skipping fetch.")
        return

    wiki_wiki = wikipediaapi.Wikipedia(WIKI_PREFIX, 'en')
    page = wiki_wiki.page(term)

    if page.exists():
        logging.info(f"Processing page: {page.title}")
        page_dict = _build_page_dict(page)
        existing_data.update(page_dict)
        FileManagement.write_to_yaml(existing_data, yaml_path)
        _add_new_redirects(page.title, f"{file_name}Redirects.csv")
        logging.info(f"Page content written to {yaml_filename}")
    else:
        logging.warning(f"No page found for '{term}'.")

def _build_page_dict(page) -> Dict[str, object]:
    """
    Constructs a dictionary representation of the Wikipedia page content.

    :param page: A Wikipedia page object.
    :return: A dictionary representing the summary and sections of the page.
    """
    infobox = _get_wikipedia_infobox(page.title)
    page_dict = {
        page.title.lower(): {
            'summary': page.summary,
            'sections': {section.title: _section_to_dict(section) for section in page.sections}
        }
    }

    if infobox:
        page_dict[page.title]['infobox'] = _infobox_to_dict(infobox)

    return page_dict

@handle_errors
def _get_wikipedia_infobox(term: str) -> Optional[str]:
    """
    Fetches the infobox for the specified Wikipedia term.

    :param term: The title of the Wikipedia page from which to fetch the infobox.
    :return: A cleaned infobox string, or None if it does not exist.
    """
    params = {
        'action': 'query',
        'prop': 'revisions',
        'rvprop': 'content',
        'rvsection': 0,  # Retrieve only the top section (infobox usually is there)
        'titles': term,
        'format': 'json',
        'formatversion': 2,
        'rvslots': 'main'
    }

    response = requests.get(WIKI_API_URL, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()

    page = data['query']['pages'][0]
    if 'revisions' in page:
        content = page['revisions'][0]['slots']['main']['content']
        infobox = _get_infobox(content)
        if infobox:
            return _clean_infobox(infobox)
        return None
    else:
        logging.info(f"Page '{term}' does not contain an infobox.")
        return None

def _get_infobox(content: str) -> Optional[str]:
    """
    Extracts the infobox from the content of a Wikipedia page.

    :param content: The complete content of the Wikipedia page.
    :return: The extracted infobox string or None.
    """
    infobox_start = content.find("{{Infobox")
    if infobox_start == -1:
        logging.info("No infobox found.")
        return None

    brace_count = 0
    index = infobox_start
    while index < len(content):
        if content[index:index+2] == "{{":
            brace_count += 1
            index += 2
        elif content[index:index+2] == "}}":
            brace_count -= 1
            index += 2
            if brace_count == 0:
                return content[infobox_start:index]
        else:
            index += 1

    return "Infobox extraction failed."

def _clean_infobox(infobox: str) -> str:
    """
    Cleans and formats the infobox for readability and minimizing tokens for language model processing.

    :param infobox: The raw infobox string.
    :return: A cleaned infobox string for easier interpretation.
    """
    # REVIEW: This just strips so much useful information as to *why* we're removing each term
    # Replace templates with their values
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)}}', r'\2 \3', infobox)
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)\|e=([^|}]+)\|u=([^|}]+)}}', r'\2e\4 \5', infobox)

    # Remove remaining template markers, links, and unnecessary formatting
    infobox = re.sub(r'{{|}}', '', infobox)
    infobox = re.sub(r'\[\[.*?\|', '', infobox)
    infobox = re.sub(r'\[\[|\]\]', '', infobox)
    infobox = re.sub(r'<.*?>', '', infobox)
    infobox = re.sub(r'\|', ':', infobox)
    infobox = re.sub(r'\s*\n\s*', '\n', infobox)

    return infobox.strip()

def _infobox_to_dict(text: str) -> Dict[str, object]:
    """
    Converts the infobox text into dictionary format for structured representation.

    :param text: The infobox text to convert.
    :return: A dictionary representation of the infobox contents.
    """
    result = {}
    current_key = None
    current_list = None

    for line in text.splitlines():
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        if line.startswith(":"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().strip(":").strip()
                value = value.strip()
                if value == "plainlist :":
                    current_key = key
                    current_list = []
                    result[current_key] = current_list
                else:
                    result[key] = value
                    current_key = None
                    current_list = None
            else:
                if current_list is not None:
                    current_list.append(line.strip(":").strip())
        elif current_list is not None:
            current_list.append(line)

    return result

def _add_new_redirects(term: str, redirect_file: str) -> None:
    """
    Fetches the redirects for a given page and appends them to a specified CSV file.

    :param term: The title of the Wikipedia page to fetch redirects for.
    :param redirect_file: The path to the CSV file where redirects will be saved.
    """
    redirects = _get_redirects(term)
    logging.info(f"Redirects found: {redirects}")

    if redirects:
        redirect_dicts = [{'redirect_term': redirect, 'target_term': term} for redirect in redirects]
        fieldnames = ['redirect_term', 'target_term']
        FileManagement.write_to_csv(redirect_file, redirect_dicts, fieldnames)
    else:
        logging.info(f"No redirects found for {term}.")

@handle_errors
def _get_redirects(term: str) -> List[str]:
    """
    Uses the MediaWiki API to fetch the redirect history for the specified Wikipedia page.

    :param term: The title of the Wikipedia page to check for redirects.
    :return: A list of titles for pages that redirect to the specified page.
    """
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'backlinks',
        'blfilterredir': 'redirects',
        'bltitle': term,  # REVIEW: Removing these comments is not helpful
        'bllimit': 'max'
    }

    response = requests.get(WIKI_API_URL, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()

    redirects = []
    if 'query' in data and 'backlinks' in data['query']:
        redirects = [link['title'] for link in data['query']['backlinks']]
    return redirects

if __name__ == "__main__":
    term = input("Enter a search term: ")
    search_wikipedia_api(term)

```

## UserContextManagement.py
```python
import logging
import re
from typing import List, Dict, Any
from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface


class UserContextManagement(EncyclopediaManagementInterface):
    """
    UserContextManagement: A class for managing user-specific terms
    extracted from interactions, enabling retrieval of user context.
    
    This class implements a singleton pattern to ensure only a single
    instance exists in memory.
    """

    _instance = None
    # Precompiled regex pattern for extracting user topic tags
    TAG_PATTERN = re.compile(
        r'<(?P<node_name>[a-zA-Z_]+)\s+parameter="(?P<parameter>[^"]+)"\s+content="(?P<content>[^"]+)"\s*/>'
    )

    def __new__(cls) -> "UserContextManagement":
        """Ensures a single instance of UserContextManagement."""
        if cls._instance is None:
            cls._instance = super(UserContextManagement, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def extract_terms_from_input(user_input: List[str]) -> List[Dict[str, Any]]:
        """Extracts user_topic contextual information based on user input.

        :param user_input: The input text provided by the user.
        :return: A list of dictionaries containing extracted terms and their respective content.
        """
        # REVIEW: Doesn't appear to be aware that changing the instructions to no longer explicietly mention the desired format would increase failure rates
        instructions = (
            "For the given prompt, explain your reasoning step by step. "
            "Identify and return an array of specific, concise items that describe personal context that can be inferred. "
            "Only infer information if it seems beneficial to the user’s question or future questions. "
            "Node name and parameter should ideally be singular words or contain underscores. "
            "Your chosen name should focus on the root semantic concept. "
            "Required: node_name, parameter, content; all three must be included."
        )

        user_topics_reasoning = AiOrchestrator().execute(
            [instructions],
            user_input,
        )

        logging.info(f"user topic reasoning: {user_topics_reasoning}")
        parsed_terms = UserContextManagement.parse_user_topic_tags(user_topics_reasoning)
        logging.info(f"parsed terms: {parsed_terms}")

        return parsed_terms

    @staticmethod
    def parse_user_topic_tags(input_text: str) -> List[Dict[str, str]]:
        """Parses user topic tags from input text.

        :param input_text: The input text containing user topic tags.
        :return: A list of dictionaries with node names, parameters, and content.
        """
        matches = UserContextManagement.TAG_PATTERN.findall(input_text)  # Extract all matches from input_text

        if not matches:
            logging.warning("No matches found for user topic tags.")

        # Create a list of dictionaries from matches
        tags = [{
            "node": match[0],
            "parameter": match[1],
            "content": match[2]
        } for match in matches]

        return tags

    @staticmethod
    def validate_term(key: str, value: str) -> None:
        """Validates the term before adding it to the encyclopedia.

        :param key: The key of the term to validate.
        :param value: The content associated with the term.
        :raises ValueError: If the key or value is deemed invalid.
        """
        if not key or not value:
            raise ValueError("Term key and value cannot be empty.")
        if len(key) > 100:  # Arbitrary length restriction
            raise ValueError("Term key is too long.")
        if len(value) > 50000:  # Arbitrary content restriction
            raise ValueError("Term content is too long.")

if __name__ == '__main__':
    encyclopediaManagement = UserContextManagement()
    sample_text = r"""
    <user_name parameter="first_name" content="John"/> 
    <user_name parameter="last_name" content="Doe"/>  # REVIEW: The fact it wants to change my arbitrary examples is kinda funny
    <user_name parameter="gender" content="male"/>
    """
    print(encyclopediaManagement.parse_user_topic_tags(sample_text))

```

## Pricing.py
```python
import logging
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB

class Pricing:
    """
    Pricing management class for handling user balances and session costs.
    """

    @staticmethod
    def get_user_balance() -> float:
        """Retrieves the current balance for the user.
        
        :return: The user's balance.
        """
        return NodeDB().get_user_balance()

    @staticmethod
    def top_up_user_balance(amount: float) -> dict:
        """Tops up the user's balance.
        
        :param amount: The amount by which to top up the balance.
        :return: A dictionary containing the status code and message.
        """
        try:
            NodeDB().update_user_balance(amount)
            return {
                "status_code": 200,
                "message": f"User balance successfully topped up by ${amount:.2f}."
            }
        except Exception as e:
            logging.exception(f"Failed to update user balance: {str(e)}")
            return {
                "status_code": 500,
                "message": f"Failed to update user balance: {str(e)}"
            }

    @staticmethod
    def get_session_cost() -> float:
        """Fetches the current session cost accumulated since deployment.
        
        :return: The current session cost.
        """
        return Globals.current_request_cost


```

## NodeDatabaseManagement.py

```python
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
from Utilities.Contexts import get_user_context, get_message_context


class NodeDatabaseManagement:
    """
    Singleton class for managing interactions with the Neo4j database.
    # REVIEW: Still deleting to do comments without acting on them, probably mostly because its mini

    This class ensures that all database interactions are encapsulated and allows  # REVIEW: Not a fan
    for a single instance to manage connections and transactions with the database.
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
        """Initializes the Neo4j driver."""
        if not hasattr(self, 'neo4jDriver'):  # Prevent reinitialization
            self.neo4jDriver = Neo4jDriver()

    # User Management Methods

    def create_user(self, user_id: str, email: str, password_hash: str) -> bool:
        """Creates a new user in the database.
        
        :param user_id: The unique identifier for the user.
        :param email: The user's email address.
        :param password_hash: The hashed password of the user.
        :return: True if the user was created successfully, False otherwise.
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
            return True
        return False

    def user_exists(self, email: str) -> bool:
        """Checks if a user exists with the given email.
        
        :param email: The email to check for user existence.
        :return: True if the user exists, False otherwise.
        """
        parameters = {"email": email}
        result = self.neo4jDriver.execute_read(
            CypherQueries.FIND_USER_BY_EMAIL,
            parameters
        )
        return bool(result)

    def find_user_by_email(self, email: str) -> str:
        """Finds the user ID associated with the provided email.
        
        :param email: The email address of the user.
        :return: The user ID.
        :raises ValueError: If multiple users are found with the same email.
        """
        parameters = {"email": email}
        records = self.neo4jDriver.execute_read(
            CypherQueries.FIND_USER_BY_EMAIL,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database Catastrophe: Shared email address [{email}]!")
            raise ValueError(f"Multiple users found for email: {email}")

        return records[0]["user_id"]

    def get_user_password_hash(self, user_id: str) -> str:
        """Retrieves the hashed password for a given user ID.
        
        :param user_id: The unique identifier for the user.
        :return: The hashed password.
        :raises ValueError: If multiple users are found with the same ID.
        """
        parameters = {"user_id": user_id}
        records = self.neo4jDriver.execute_read(
            CypherQueries.GET_USER_PASSWORD_HASH,
            parameters
        )

        if len(records) > 1:
            logging.error(f"Database Catastrophe: These UUIDs aren't unique! [{user_id}]!")
            raise ValueError(f"Multiple user records found for ID: {user_id}")

        return records[0]["password_hash"]

    # Messages Handling

    def get_message_by_id(self, message_id: str) -> Dict[str, str]:
        """Retrieves a message by its ID.
        
        :param message_id: The unique identifier of the message.
        :return: The details of the message.
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
        """Creates a USER_PROMPT node in the database and associates a file with it.
        
        :param category: The category for the prompt.
        :param user_prompt: The user prompt content.
        :param llm_response: The response generated by the language model.
        :return: The category associated with the new user prompt node.
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
            CypherQueries.POPULATE_USER_PROMPT_NODE,
            parameters,
            "user_prompt_id"
        )

        self.create_file_nodes_for_user_prompt(user_prompt_id, category)
        return category

    # REVIEW: get_messages_by_category was deleted for no reason???

    # REVIEW: delete_message_by_id was deleted for no reason???

    # Categories Handling

    def create_category(self, category_name: str) -> None:
        """Creates a new category in the database.
        
        :param category_name: The name of the new category.
        """
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
        """Retrieves the ID of the specified category.
        
        :param category_name: The name of the category.
        :return: The unique identifier of the category.
        """
        parameters = {"category_name": category_name}
        records = self.neo4jDriver.execute_read(CypherQueries.GET_CATEGORY_ID, parameters)
        category_id = records[0]["category_id"]

        logging.info(f"Category id for {category_name}: {category_id}")
        return category_id

    def list_categories(self) -> List[str]:
        """Lists all unique categories associated with the user.
        
        :return: A list of category names.
        """
        parameters = {"user_id": get_user_context()}
        records = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES, parameters)
        return [record["category_name"] for record in records]

    # REVIEW: list_categories_with_files was deleted for no reason??? Probably because the context limit is too small for mini

    # Files Handling

    def create_file_nodes_for_user_prompt(self, user_prompt_id: str, category: str) -> None:
        """Creates file nodes for the specified user prompt.
        
        :param user_prompt_id: The ID of the user prompt.
        :param category: The category associated with the files.
        """
        file_names = StorageMethodology.select().list_staged_files()
        for file_name in file_names:
            self.create_file_node(user_prompt_id, category, file_name)

    def create_file_node(self, user_prompt_id: str, category: str, file_path: str) -> None:
        """Creates a file node in the database representing a specific file.
        
        :param user_prompt_id: The ID of the user prompt associated with this file.
        :param category: The category the file belongs to.
        :param file_path: The path to the file.
        """
        try:
            time = int(datetime.now().timestamp())
            file_name = os.path.basename(file_path)
            content = StorageMethodology.select().read_file(file_path)

            summary = AiOrchestrator().execute(
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

            logging.info(
                f"Creating file node: {category}/{file_name} against prompt [{user_prompt_id}]\nsummary: {summary}")

            self.neo4jDriver.execute_write(CypherQueries.CREATE_FILE_NODE, parameters)
        except Exception as e:
            logging.exception("Failed to save file node", exc_info=e)


if __name__ == '__main__':
    pass  # Placeholder if you want to execute testing

# REVIEW: Note in or around 300 lines it just gives up and deletes all code past its context limit

```

## Neo4jDriver.py

Perfectly fine, just some documentation suggestions

```python
import logging
import os
from neo4j import GraphDatabase, basic_auth
from Utilities.Decorators import handle_errors
from typing import Optional, Any, Dict, List

class Neo4jDriver:
    """
    A class that encapsulates the Neo4j database driver and provides methods to interact with the database.
    
    # REVIEW: Means the same thing?
    This class manages the connection to the Neo4j database and provides read and write functionalities.
    """

    def __init__(self):
        """Initializes the Neo4j driver using environment variables for configuration."""
        uri = os.getenv("NEO4J_URI")
        password = os.getenv("NEO4J_PASSWORD")
        if not uri or not password:
            raise ValueError("NEO4J_URI and NEO4J_PASSWORD environment variables must be set.")
        
        self.driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", password))

    def close(self) -> None:
        """Closes the database driver connection."""
        if self.driver:
            self.driver.close()

    @handle_errors(debug_logging=True)
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None, field: Optional[str] = None) -> Any:
        """
        Executes a write transaction in the database.

        :param query: The actual Cypher query to execute.
        :param parameters: The parameters required for the execution of the query.
        :param field: Optional field to RETURN.
        :return: The value extracted from the query result if a field is specified.
        """
        with self.driver.session() as session:
            return session.write_transaction(
                lambda tx: self._extract_field(tx.run(query, parameters), field)
            )

    @staticmethod
    def _extract_field(result, field: Optional[str]) -> Optional[Any]:
        """
        Extracts a field from the query result.

        :param result: The result set from the executed query.
        :param field: The name of the field to be extracted.
        :return: The value of the specified field or None if not found.
        """
        record = result.single()
        if record is None:
            logging.error("No record returned by the query.")
            return None

        logging.info(f"Record returned: {record}")
        try:
            value = record.get(field)
            logging.info(f"Field '{field}' value: {value}")
            return value
        except KeyError:
            logging.error(f"Field '{field}' not found in the record.")
            return None

    @handle_errors()
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a read transaction in the database.

        :param query: The Cypher query to execute.
        :param parameters: Optional parameters for the query.
        :return: A list of records returned by the query.
        """
        with self.driver.session() as session:
            return session.read_transaction(lambda tx: list(tx.run(query, parameters)))

    @handle_errors(debug_logging=True, raise_errors=True)
    def execute_delete(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Executes a delete operation in the database.

        :param query: The Cypher query for the delete operation.
        :param parameters: Optional parameters for the query.
        """
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run(query, parameters))
            logging.info(f"Successfully executed delete operation: {query} with params: {parameters}")

```

## EncyclopediaManagementInterface.py

Abominable, imports are broken unnecessarily, good coding practice is reverted, not even worth reviewing

```python
import logging
import os
from typing import Dict, Any

class EncyclopediaManagementInterface:
    """
    Manages encyclopedia data files and provides search and retrieval capabilities.

    This class facilitates loading encyclopedia entries and redirects, searching for terms,
    and summarizing information relevant to user queries.
    """

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    ENCYCLOPEDIA_NAME = "To Define"
    DEFAULT_INSTRUCTIONS = "To Define"

    _instance = None

    def __new__(cls) -> "EncyclopediaManagementInterface":
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagementInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the EncyclopediaManagementInterface.
        """
        if not hasattr(self, "initialized"):  # Prevent reinitialization
            self.encyclopedia: Dict[str, str] = {}
            self.redirects: Dict[str, str] = {}

            # Initialize file paths
            self.encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + self.ENCYCLOPEDIA_EXT)
            self.redirect_encyclopedia_path = os.path.join(self.data_path, self.ENCYCLOPEDIA_NAME + self.REDIRECTS_EXT)
            self.initialized = True

    def load_encyclopedia_data(self) -> None:
        """Load encyclopedia and redirect data from the specified files."""
        try:
            self.encyclopedia = self._load_yaml_file(self.encyclopedia_path)
            self.redirects = self._load_redirects(self.redirect_encyclopedia_path)
            logging.info("Encyclopedia and redirects loaded successfully")
        except Exception as e:
            logging.error(f"Error loading encyclopedia data: {str(e)}")

    @staticmethod
    def _load_yaml_file(filepath: str) -> Dict[str, str]:
        """Load a YAML file and return its content."""
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}

    @staticmethod
    def _load_redirects(filepath: str) -> Dict[str, str]:
        """Load redirect terms from a CSV file and return them as a dictionary."""
        redirects_df = pd.read_csv(filepath, header=None, names=['redirect_term', 'target_term'])
        return redirects_df.set_index('redirect_term')['target_term'].to_dict()

    @handle_errors(raise_errors=True)
    def search_encyclopedia(self, user_messages: List[str]) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: The user input messages containing the terms.
        :return: A string representation of the additional context found.
        """
        # Logic for searching the encyclopedia should be implemented

    def extract_terms_from_encyclopedia(self, terms: List[Dict[str, Any]]) -> str:
        """Search for a set of terms in the encyclopedia.

        :param terms: The terms to check in the encyclopedia.
        :return: A string representation of additional context extracted.
        """
        # Logic for extracting terms from encyclopedia should be implemented

    def validate_term(self, key: str, value: str) -> None:
        """Validates the term before adding it to the encyclopedia.

        :param key: The key of the term to validate.
        :param value: The content associated with the term.
        :raises ValueError: If the key or value is deemed invalid.
        """
        if not key or not value:
            raise ValueError("Term key and value cannot be empty.")
        if len(key) > 100:
            raise ValueError("Term key is too long.")
        if len(value) > 50000:
            raise ValueError("Term content is too long.")

if __name__ == '__main__':
    pass  # This file is intended to be imported, not executed directly.

```

## EncylopediaManagement.py

Likewise awful, strips the class away - which isn't the point of the file.
```python
import logging
import os
import wikipediaapi  # Make sure to install wikipedia-api package
from typing import Dict, Optional
from Data.Files.FileManagement import FileManagement
from Utilities.Decorators import handle_errors

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../UserData/DataStores')
ENCYCLOPEDIA_NAME = "Encyclopedia"
REDIRECTS_FILENAME = f"{ENCYCLOPEDIA_NAME}Redirects.csv"
YAML_EXTENSION = ".yaml"

def _section_to_dict(section) -> Dict[str, object]:
    """
    Recursively convert section and its subsections to a dictionary.

    :param section: The section of the Wikipedia page to convert.
    :return: A dictionary representation of the section.
    """
    section_dict = {'content': section.text}
    if section.sections:
        section_dict['subsections'] = {
            subsection.title: _section_to_dict(subsection) for subsection in section.sections
        }
    return section_dict

@handle_errors
def search_wikipedia_api(term: str) -> None:
    """
    Fetches a Wikipedia page for the given term and caches the content in a local Encyclopedia cache.

    If the page content already exists, it skips the fetch and logs a message.

    :param term: The title of the Wikipedia page to fetch.
    """
    yaml_filename = f"{term}.yaml"
    yaml_path = os.path.join(DATA_PATH, yaml_filename)

    existing_data = FileManagement.load_yaml(yaml_path)

    if term in existing_data:
        logging.info(f"Data for '{term}' is already present in {yaml_filename}. Skipping fetch.")
        return

    wiki_wiki = wikipediaapi.Wikipedia('ThinkerBot (https://github.com/AaronFR/Thinker)', 'en')
    page = wiki_wiki.page(term)

    if page.exists():
        logging.info(f"Processing page: {page.title}")
        page_dict = _build_page_dict(page)

        existing_data.update(page_dict)
        FileManagement.write_to_yaml(existing_data, yaml_path)
        _add_new_redirects(page.title, os.path.join(DATA_PATH, REDIRECTS_FILENAME))
        logging.info(f"Page content written to {yaml_filename}")
    else:
        logging.warning(f"No page found for '{term}'.")

def _build_page_dict(page) -> Dict[str, object]:
    """
    Constructs a dictionary representation of the Wikipedia page content.

    :param page: A Wikipedia page object.
    :return: A dictionary representing the summary and sections of the page.
    """
    infobox = _get_wikipedia_infobox(page.title)
    page_dict = {
        page.title.lower(): {
            'summary': page.summary,
            'sections': {section.title: _section_to_dict(section) for section in page.sections}
        }
    }

    if infobox:
        page_dict[page.title]['infobox'] = _infobox_to_dict(infobox)

    return page_dict

@handle_errors
def _get_wikipedia_infobox(term: str) -> Optional[str]:
    """
    Fetches the infobox for the specified Wikipedia term.

    :param term: The title of the Wikipedia page from which to fetch the infobox.
    :return: A cleaned infobox string, or None if it does not exist.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'prop': 'revisions',
        'rvprop': 'content',
        'rvsection': 0,
        'titles': term,
        'format': 'json',
        'formatversion': 2,
        'rvslots': 'main'
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    page = data['query']['pages'][0]
    if 'revisions' in page:
        content = page['revisions'][0]['slots']['main']['content']
        infobox = _get_infobox(content)
        return _clean_infobox(infobox) if infobox else None
    else:
        logging.info(f"Page '{term}' does not contain an infobox.")
        return None

def _get_infobox(content: str) -> Optional[str]:
    """
    Extracts an infobox from the content of a Wikipedia page.

    :param content: The complete content of the Wikipedia page.
    :return: The extracted infobox string or None.
    """
    infobox_start = content.find("{{Infobox")
    if infobox_start == -1:
        logging.info(f"No infobox found")
        return None

    brace_count = 0
    index = infobox_start
    while index < len(content):
        if content[index:index+2] == "{{":
            brace_count += 1
            index += 2
        elif content[index:index+2] == "}}":
            brace_count -= 1
            index += 2
            if brace_count == 0:
                return content[infobox_start:index]
        else:
            index += 1

    return "Infobox extraction failed."

def _clean_infobox(infobox: str) -> str:
    """
    Cleans and formats the infobox for readability.

    :param infobox: The raw infobox string.
    :return: A cleaned infobox string.
    """
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)}}', r'\2 \3', infobox)
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)\|e=([^|}]+)\|u=([^|}]+)}}', r'\2e\4 \5', infobox)
    infobox = re.sub(r'{{|}}', '', infobox)  # Remove remaining {{ and }}
    infobox = re.sub(r'\[\[.*?\|', '', infobox)  # Remove link text
    infobox = re.sub(r'\[\[|\]\]', '', infobox)  # Remove remaining [[ and ]]
    infobox = re.sub(r'<.*?>', '', infobox)  # Remove other HTML tags
    infobox = re.sub(r'\|', ':', infobox)  # Replace pipes with colons for readability
    infobox = re.sub(r'\s*\n\s*', '\n', infobox)  # Clean up extra newlines
    return infobox.strip()  # Strip leading/trailing spaces

def _infobox_to_dict(text: str) -> Dict[str, object]:
    """
    Converts the infobox text into dictionary format.

    :param text: The infobox text to convert.
    :return: A dictionary representation of the infobox contents.
    """
    result = {}
    current_key, current_list = None, None

    for line in text.splitlines():
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        if line.startswith(":") and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip().strip(":")
            value = value.strip()
            if value == "plainlist :":
                current_key = key
                current_list = []
                result[current_key] = current_list
            else:
                result[key] = value
                current_key, current_list = None, None
        elif current_list is not None:
            current_list.append(line.strip(":").strip())

    return result

def _add_new_redirects(term: str, redirect_file: str) -> None:
    """
    Fetches the redirects for a given page and appends them to a specified CSV file.

    :param term: The title of the Wikipedia page to fetch redirects for.
    :param redirect_file: The path to the CSV file where redirects will be saved.
    """
    redirects = _get_redirects(term)
    logging.info(f"Redirects found: {redirects}")

    if redirects:
        redirect_dicts = [{'redirect_term': redirect, 'target_term': term} for redirect in redirects]
        fieldnames = ['redirect_term', 'target_term']
        FileManagement.write_to_csv(redirect_file, redirect_dicts, fieldnames)
    else:
        logging.info(f"No redirects found for {term}.")

@handle_errors
def _get_redirects(term: str) -> List[str]:
    """
    Uses the MediaWiki API to fetch the redirect history for the specified Wikipedia page.

    :param term: The title of the Wikipedia page to check for redirects.
    :return: A list of titles for pages that redirect to the specified page.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'backlinks',
        'blfilterredir': 'redirects',
        'bltitle': term,
        'bllimit': 'max'
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()

    redirects = []
    if 'query' in data and 'backlinks' in data['query']:
        redirects = [link['title'] for link in data['query']['backlinks']]
    return redirects

if __name__ == "__main__":
    term = input("Enter a search term: ")
    search_wikipedia_api(term)

```

## CypherQueries.py

Tolerable but I don't agree with how it re-categorised and re-arranged the queries.
```python
"""
CypherQueries.py

This module contains Cypher queries used for interacting with the Neo4j Graph Database.

# REVIEW: The constraints contain valuable information about the db 
"""

# User Management Queries

FIND_USER_BY_EMAIL = """
MATCH (user:USER)
WHERE user.email = $email
RETURN user.id AS user_id
"""

GET_USER_PASSWORD_HASH = """
MATCH (user:USER)
WHERE user.id = $user_id
RETURN user.password_hash AS password_hash
"""

CREATE_USER = """
MERGE (user:USER {id: $user_id})
ON CREATE SET user.email = $email, user.password_hash = $password_hash, user.balance = 0
RETURN user.id
"""

# Category Management Queries

CREATE_CATEGORY = """
MATCH (user:USER {id: $user_id})
WITH user
MERGE (category:CATEGORY {name: $category_name})
ON CREATE SET category.id = $category_id
MERGE (user)-[:HAS_CATEGORY]->(category)
RETURN category.id AS category_id
"""

GET_CATEGORY_ID = """
MATCH (category:CATEGORY {name: $category_name})
RETURN category.id AS category_id
"""

LIST_CATEGORIES = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)
RETURN DISTINCT category.name AS category_name
ORDER BY category_name
"""

LIST_CATEGORIES_WITH_FILES = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)--(file:FILE)
RETURN DISTINCT category.name AS category_name
ORDER BY category_name
"""

# Message Management Queries

CREATE_USER_TOPIC = """
MATCH (user:USER {id: $user_id})
WITH user
MERGE (user_topic:USER_TOPIC {name: $node_name})
SET user_topic.{parameter} = $content
MERGE (user_topic)-[:RELATES_TO]->(user)
RETURN id(user_topic) AS user_topic_id
"""

SEARCH_FOR_USER_TOPIC = """
MATCH (user:USER {id: $user_id})
WITH user
MATCH (user_topic:USER_TOPIC {name: $node_name})
RETURN properties(user_topic) AS all_properties
"""

GET_MESSAGE = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)
    <-[:BELONGS_TO]-(user_prompt:USER_PROMPT {id: $message_id})
RETURN user_prompt.id AS id, user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time
"""

GET_MESSAGES = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY {name: $category_name})
    <-[:BELONGS_TO]-(user_prompt:USER_PROMPT)
RETURN user_prompt.id AS id, user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time
ORDER BY user_prompt.time DESC
"""

# File Management Queries

CREATE_FILE_NODE = """
MATCH (user:USER {id: $user_id})
MERGE (category:CATEGORY {name: $category})
WITH user, category
MATCH (user_prompt:USER_PROMPT)
WHERE user_prompt.id = $user_prompt_id
CREATE (file:FILE {name: $name, time: $time, summary: $summary, structure: $structure, version: 1})
MERGE (file)-[:ORIGINATES_FROM]->(user_prompt)
MERGE (file)-[:BELONGS_TO]->(category)
RETURN file
"""

DELETE_MESSAGE_AND_POSSIBLY_CATEGORY = """
MATCH (message:USER_PROMPT)-[:BELONGS_TO]->(category:CATEGORY)<-[:HAS_CATEGORY]-(user:USER {id: $user_id})
WHERE message.id = $message_id
DETACH DELETE message
WITH category
OPTIONAL MATCH (category)<-[:BELONGS_TO]-(remaining_messages:USER_PROMPT)
WITH category, count(remaining_messages) AS remaining_count
WHERE remaining_count = 0
DETACH DELETE category
"""

# Pricing Queries

GET_USER_BALANCE = """
MATCH (user:USER {id: $user_id})
RETURN user.balance AS balance
"""

UPDATE_USER_BALANCE = """
MATCH (user:USER {id: $user_id})
SET user.balance = user.balance + $sum
"""

# Receipt Management Queries

CREATE_RECEIPT = """
CREATE (receipt:RECEIPT {input_costs: $input_costs, output_costs: $output_costs, mode: $mode})
WITH receipt
MATCH (user:USER {id: $user_id})
CREATE (receipt)-[:BELONGS_TO]->(user)
WITH receipt
OPTIONAL MATCH (prompt:USER_PROMPT {id: $message_id})
FOREACH(_ IN CASE WHEN prompt IS NOT NULL THEN [1] ELSE [] END |
    CREATE (prompt)-[:ASSOCIATES_WITH]->(receipt)
)
RETURN receipt
"""


```

## Configuration.py

Deletes load_config unnecessarily, the singleton idea is theorectically nice but all the existing methods are static. Why?


```python
import logging
import os
import yaml
from typing import Dict, Any

from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Decorators import handle_errors

class Configuration:
    """
    Configuration class to manage loading and updating configuration settings
    from YAML and CSV files. This includes support for deep merging of
    configurations and handling user-specific settings.
    """

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    ENCYCLOPEDIA_NAME = "To Define"
    instructions = "To Define"

    _instance = None

    def __new__(cls) -> "Configuration":
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the Configuration instance and ensures that it only initializes once.
        """
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.encyclopedia: Dict[str, str] = {}
            self.redirects: Dict[str, str] = {}

            self.encyclopedia_path = self._get_encyclopedia_path()
            self.redirect_encyclopedia_path = self._get_redirect_encyclopedia_path()

            self.initialized = True

    def load_encyclopedia_data(self) -> None:
        """Load encyclopedia and redirect data from the specified files."""
        try:
            self.encyclopedia = self._load_yaml_file(self.encyclopedia_path)
            self.redirects = self._load_redirects(self.redirect_encyclopedia_path)
            logging.info("Encyclopedia and redirects loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load encyclopedia data: {e}")

    @staticmethod
    @handle_errors(raise_errors=True)
    def _load_yaml_file(filepath: str) -> Dict[str, str]:
        """Load a YAML file and return its content."""
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}

    @staticmethod
    @handle_errors(raise_errors=True)
    def _load_redirects(filepath: str) -> Dict[str, str]:
        """Load redirect terms from a CSV file and return them as a dictionary."""
        redirects_df = StorageMethodology.load_csv(filepath)
        return redirects_df.set_index('redirect_term')['target_term'].to_dict()

    @handle_errors(raise_errors=True)
    def update_config_field(self, field_path: str, value: Any) -> None:
        """
        Updates a particular field in the user's YAML configuration file.
        If it's the first time changing, a new user config file will be created automatically.

        :param field_path: The dot-separated path to the field to update.
        :param value: The value to set for the specified field.
        """
        user_config_path = os.path.join(get_user_context() + ".yaml")
        config = self.load_yaml(user_config_path)

        # Navigate to the specified field and update the value
        keys = field_path.split('.')
        current = config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

        # Save the updated configuration back to the YAML file
        # REVIEW: Doesn't appear to know storage methology is just a interface
        StorageMethodology.save_yaml(user_config_path, config)

    def _get_encyclopedia_path(self) -> str:
        """Get the path for the encyclopedia YAML file."""
        return os.path.join('path', 'to', 'your', 'encyclopedia', f"{self.ENCYCLOPEDIA_NAME}{self.ENCYCLOPEDIA_EXT}")

    def _get_redirect_encyclopedia_path(self) -> str:
        """Get the path for the redirects CSV file."""
        return os.path.join('path', 'to', 'your', 'redirects', f"{self.ENCYCLOPEDIA_NAME}{self.REDIRECTS_EXT}")



if __name__ == '__main__':
    config = Configuration()
    config_items = config.load_encyclopedia_data()
    print(config_items)

```

## CategoryManagement.py

Finally, some actually good code refactoring suggestions.
Doesn't quite pick up on the fact that user_categorisation_instructions are extracting a user defined value not specifying one

```python
import logging
import os
import re
from typing import Optional, List, Dict

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Data.Files.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context

class CategoryManagement:
    """
    Manages the automatic categorization of uploaded files by the user and files created by the system.
    This class implements the singleton pattern to ensure a single instance only exists.
    """

    _instance = None
    CATEGORIZATION_TEMPLATE = "<user prompt>{}</user prompt>\n<response>{}</response>"
    INSTRUCTION_TEMPLATE = (
        "LIGHTLY suggested existing categories, you DONT need to follow: {}"
        "Given the following prompt-response pair, think through step by step, explaining your reasoning "
        "and categorize the data with the most suitable single-word answer. "
        "Write it as <result=\"(your_selection)\""
    )
    INVALID_CATEGORY_MSG = "Failure to categorize! Invalid category provided."

    def __new__(cls):
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(CategoryManagement, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def categorise_prompt_input(user_prompt: str, llm_response: Optional[str] = None, creating: bool = True) -> Optional[str]:
        """
        Categorize the user prompt input based on existing categories and generate new categories if needed.

        :param user_prompt: The input prompt string.
        :param llm_response: The optional llm response for additional context.
        :param creating: Flag indicating whether a new category should be created.
        :return: The name of the selected category or None if categorization fails.
        """
        categories = nodeDB().list_categories()
        config = Configuration.load_config()

        categorisation_input = CategoryManagement.CATEGORIZATION_TEMPLATE.format(user_prompt, llm_response or "")
        categorisation_instructions = CategoryManagement.INSTRUCTION_TEMPLATE.format(categories)

        category_reasoning = AiOrchestrator().execute([categorisation_instructions], [categorisation_input])
        logging.info(f"Category Reasoning: {category_reasoning}")

        category = CategoryManagement.extract_example_text(category_reasoning)
        if not category:
            logging.warning(CategoryManagement.INVALID_CATEGORY_MSG)
            return None
        
        return CategoryManagement.possibly_create_category(category)

    @staticmethod
    def possibly_create_category(category: str) -> str:
        """
        If the category does not already exist in the node database, it creates a new category.

        :param category: The category to possibly be added to the node database.
        :return: The actual category name.
        """
        categories = nodeDB().list_categories()
        if category not in categories:
            nodeDB().create_category(category)
        return category

    @staticmethod
    def extract_example_text(input_string: str) -> Optional[str]:
        """
        Extracts the text contained within the result element.

        :param input_string: The string containing the result element.
        :return: The text inside the result element or None if not found.
        """
        match = re.search(r'<result="([^"]+)">', input_string)
        # REVIEW: This code is rather 'smart' but harder to read. Which isn't
        logging.warning(CategoryManagement.INVALID_CATEGORY_MSG) if not match else None
        return match.group(1) if match else None

    @staticmethod
    def stage_files(category: Optional[str] = None) -> None:
        """
        Stages files into a specific category based on the user prompt.

        This method retrieves files from the staging area, summarizes them, and categorizes them according to their content
        with the help of an AI orchestrator.

        :param category: If defined, the system will categorize the staged files with the given category, otherwise a category will be generated.
        """
        files = StorageMethodology.select().list_staged_files()
        if not files:
            logging.info("No files to stage.")
            return
        
        category_id = CategoryManagement._return_id_for_category(category)
        logging.info(f"Category selected: [{category_id}] - {category}")

        try:
            for file in files:
                staged_file_path = os.path.join(file)
                new_file_path = os.path.join(str(category_id), os.path.basename(file))
                StorageMethodology.select().move_file(staged_file_path, new_file_path)
            logging.info(f"All files moved to category: {category_id}.")
        except Exception as e:
            logging.error(f"ERROR: Failed to move all files to folder: {category_id}. Error: {str(e)}")

    @staticmethod
    def _return_id_for_category(category_name: str) -> Optional[str]:
        """
        Retrieves the ID for the specified category, creating a new category if necessary.

        :param category_name: The name of the category associated with an existing category ID.
        :return: The category ID if found, otherwise None.
        """
        category_id = nodeDB().get_category_id(category_name)
        if not category_id:
            CategoryManagement._add_new_category(category_id)
            logging.info(f"Created new category with ID [{category_id}] - {category_name}")

        return category_id

    @staticmethod
    def _add_new_category(category_id: str) -> None:
        """
        Creates the folder to store files against a given category.

        :param category_id: The new folder category ID to create.
        """
        new_directory = os.path.join(FileManagement.file_data_directory, category_id)
        os.makedirs(new_directory, exist_ok=True)  # Create new folder for the given id
        logging.info(f"Category directory created at: {new_directory}")

    @staticmethod
    def determine_category(user_prompt: str, tag_category: Optional[str] = None) -> str:
        """
        Determine the category for the user prompt.

        :param user_prompt: The user's input prompt.
        :param tag_category: The optional category tag from the front end.
        :return: The determined category.
        """
        if not tag_category:
            category = CategoryManagement.categorise_prompt_input(user_prompt)
            logging.info(f"Prompt categorised: {category}")
            return category or ''
        return tag_category


if __name__ == '__main__':
    CategoryManagement().stage_files("Put this file in Notes please")

```
