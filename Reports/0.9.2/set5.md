# Outputs for Base System Message

All of my comments will be prefaced  # REVIEW: 

## WikipediaApi.py
```python
import logging
import os
import regex as re
import requests
import wikipediaapi

from typing import Dict, Optional, List

from Data.Files.FileManagement import FileManagement
from Utilities.Decorators import handle_errors

# Set the data path for local storage
data_path = os.path.join(os.path.dirname(__file__), 'DataStores')


def _section_to_dict(section) -> Dict[str, object]:
    """
    Recursively convert section and its subsections to a dictionary.

    :param section: A section object from WikipediaAPI.
    :return: A dictionary representation of the section.
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
    yaml_path = os.path.join(data_path, yaml_filename)

    # Load existing data
    existing_data = FileManagement.load_yaml(yaml_path)
    if term in existing_data:
        logging.info(f"Data for '{term}' is already present in {yaml_filename}. Skipping fetch.")
        return

    # Fetching the page with wikipediaapi
    wiki_wiki = wikipediaapi.Wikipedia('ThinkerBot (https://github.com/AaronFR/Thinker)', 'en')
    page = wiki_wiki.page(term)

    if page.exists():
        logging.info(f"Processing page: {page.title}")

        try:
            page_dict = _build_page_dict(page)
            existing_data.update(page_dict)  # Update the existing data
            FileManagement.write_to_yaml(existing_data, yaml_path)  # Save the updated data
            _add_new_redirects(page.title, f"{file_name}Redirects.csv")  # Capture redirects
            logging.info(f"Page content written to {yaml_filename}")
        except Exception as e:
            logging.exception(f"Error while processing page '{term}': {str(e)}")
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
        'rvslots': 'main',
    }

    try:
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
    except requests.RequestException as e:
        logging.exception(f"Request failed during infobox retrieval for '{term}': {str(e)}")
        return None


def _get_infobox(content: str) -> Optional[str]:
    """
    Extracts an infobox from the content of a Wikipedia page while ensuring balanced braces.

    :param content: The complete content of the Wikipedia page.
    :return: The extracted infobox string or None if unsuccessful.
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

    logging.error("Infobox extraction failed.")
    return None  # Explicitly return None for clarity


def _clean_infobox(infobox: str) -> str:
    """
    Cleans and formats the infobox for readability and minimizing tokens for processing.

    :param infobox: The raw infobox string.
    :return: A cleaned infobox string for easier interpretation.
    """
    # Correctly handle val and convert templates, preserving value and unit
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)}}', r'\2 \3', infobox)
    infobox = re.sub(r'{{(val|convert)\|([^|]+)\|([^|}]+)\|e=([^|}]+)\|u=([^|}]+)}}', r'\2e\4 \5', infobox)

    # Remove remaining template markers and plain markers
    infobox = re.sub(r'{{|}}', '', infobox)

    # Remove internal Wikipedia links and references
    infobox = re.sub(r'\[\[.*?\|', '', infobox)
    infobox = re.sub(r'\[\[|\]\]', '', infobox)
    infobox = re.sub(r'<.*?>', '', infobox)

    # Format for easier reading
    infobox = re.sub(r'\|', ':', infobox)
    infobox = re.sub(r'\s*\n\s*', '\n', infobox).strip()

    return infobox


def _infobox_to_dict(text: str) -> Dict[str, object]:
    """
    Converts the infobox text into a structured dictionary format.

    :param text: The infobox text to convert.
    :return: A dictionary representation of the infobox contents.
    """
    result = {}
    current_key = None
    current_list = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        
        if line.startswith(":"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().strip(":")
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
        else:
            if current_list is not None:
                current_list.append(line)

    return result


def _add_new_redirects(term: str, redirect_file: str) -> None:
    """
    Fetches the redirects for a given page and appends them to a specified CSV file.

    :param term: The title of the Wikipedia page to fetch redirects for.
    :param redirect_file: The path to the CSV file where redirects will be saved.
    """
    redirects = _get_redirects(term)
    if not redirects:
        logging.info(f"No redirects found for {term}.")
        return

    redirect_dicts = [{'redirect_term': redirect, 'target_term': term} for redirect in redirects]
    fieldnames = ['redirect_term', 'target_term']
    
    try:
        FileManagement.write_to_csv(redirect_file, redirect_dicts, fieldnames)
        logging.info(f"Redirects saved for {term}: {redirect_dicts}")
    except Exception as e:
        logging.exception(f"Failed to write redirects to {redirect_file}: {str(e)}")


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

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return [link['title'] for link in data.get('query', {}).get('backlinks', [])]  # Safe access with default values
    except requests.RequestException as e:
        logging.exception(f"Request failed during redirect retrieval for '{term}': {str(e)}")
        return []


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
    **UserContextManagement**: A class for managing encyclopedia entries,
    enabling retrieval, updating, and organization of user information.

    This class implements a singleton pattern to ensure only a single instance exists.
    It facilitates the addition and management of user-specific terms extracted from interactions.
    """

    _instance = None

    def __new__(cls) -> "UserContextManagement":
        """Ensures a single instance of UserContextManagement."""
        if cls._instance is None:
            cls._instance = super(UserContextManagement, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def extract_terms_from_input(user_input: List[str]) -> List[Dict[str, Any]]:
        """Extracts contextual information from user input.

        This method processes the user input to find terms that can be used
        for future interactions. It returns a list of dictionaries containing
        extracted terms and their respective content.

        :param user_input: A list of input text strings provided by the user.
        :return: A list of dictionaries containing extracted terms and their content.
        """
        executor = AiOrchestrator()

        instructions = (
            "For the given prompt, explain your reasoning step by step. "
            "Identify and return an array of specific, concise items that describe personal context that can be inferred "
            "Only infer information if it seems beneficial to the user’s question or future questions. "
            "node_name and parameter should ideally be singular words; if not, must have underscores, not spaces. "
            "Your chosen name should reflect the root semantic concept rather than specific details. "
            "Finally, write the potential user topics as "
            "<your_selected_single_word_node_name parameter=\"(your_selected_single_word_parameter_name)\" "
            "content=\"(the content you want to note)\" />"
            "Required: tag name, parameter, content, all 3 must be included"
        )

        try:
            user_topics_reasoning = executor.execute(
                [instructions],
                user_input,
            )
            logging.info(f"User topic reasoning: {user_topics_reasoning}")

            parsed_terms = UserContextManagement.parse_user_topic_tags(user_topics_reasoning)
            logging.info(f"Parsed terms: {parsed_terms}")
            return parsed_terms
        
        except Exception as e:
            logging.exception("Failed to extract terms from user input.", exc_info=e)
            return []

    @staticmethod
    def parse_user_topic_tags(input_text: str) -> List[Dict[str, str]]:
        """Parses user topic tags from the input text.

        This method uses regex to extract node_name, parameter, and content
        from the formatted input text.

        :param input_text: A string containing user topic tags to parse.
        :return: A list of dictionaries containing node_name, parameter, and content.
        """
        pattern = r'<(?P<node_name>[a-zA-Z_]+)\s+parameter="(?P<parameter>[^"]+)"\s+content="(?P<content>[^"]+)"\s*/>'
        matches = list(re.finditer(pattern, input_text))

        if not matches:
            logging.warning("No matches found for user topic tags.")
            return []

        tags = [
            {
                "node": match.group("node_name"),
                "parameter": match.group("parameter"),
                "content": match.group("content")
            }
            for match in matches
        ]
        return tags

    @staticmethod
    def validate_term(key: str, value: str) -> None:
        """Validates the term before adding it to the encyclopedia.

        This method checks if the key and value are empty or exceed predefined lengths.

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
    # For testing purposes, this should be removed or replaced with proper unit tests.
    # Example usage, if applicable.
    example_text = r"""
    <user_name parameter="first_name" content="John" />
    <user_name parameter="last_name" content="Doe" />
    """
    print(UserContextManagement.parse_user_topic_tags(example_text))
    # This part can be commented out when integrated into the application

```

## NodeDatabaseManagement.py

```python
import logging
import threading
import os
import shortuuid
from datetime import datetime
from typing import List, Dict, Optional, Any

from Data import CypherQueries
from Data.Neo4jDriver import Neo4jDriver
from Data.Files.StorageMethodology import StorageMethodology
from Personas.PersonaSpecification import PersonaConstants
from Utilities.Contexts import get_user_context, get_message_context


class NodeDatabaseManagement:
    """
    Singleton class for managing interactions with the Neo4j database.

    This class provides methods for user management, message handling, category operations, 
    and file management within the database.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "NodeDatabaseManagement":
        """Create a singleton instance of NodeDatabaseManagement."""
        if cls._instance is None:
            with cls._lock:  # Ensure thread-safety during instance creation.
                if cls._instance is None:  # Double-check to avoid race conditions.
                    cls._instance = super(NodeDatabaseManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the Neo4j driver instance."""
        if not hasattr(self, "neo4jDriver"):  # Prevent reinitialization.
            self.neo4jDriver = Neo4jDriver()

    # User Management

    def create_user(self, user_id: str, email: str, password_hash: str) -> bool:
        """Create a new user with the provided information.

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

        try:
            returned_user_id = self.neo4jDriver.execute_write(
                CypherQueries.CREATE_USER,
                parameters,
                "user.id"
            )

            if returned_user_id:
                StorageMethodology.select().add_new_user_file_folder(returned_user_id)
                logging.info(f"User created successfully: {user_id}")
                return True
        except Exception as e:
            logging.error(f"Failed to create user: {user_id}, error: {e}")

        return False

    def user_exists(self, email: str) -> bool:
        """Check if a user with the given email exists.

        :param email: The email to check.
        :return: True if the user exists, False otherwise.
        """
        parameters = {"email": email}

        try:
            result = self.neo4jDriver.execute_read(
                CypherQueries.FIND_USER_BY_EMAIL,
                parameters
            )
            return bool(result)  # Return False if no user is found.
        except Exception as e:
            logging.error(f"Error checking user existence for email: {email}, error: {e}")

        return False

    def find_user_by_email(self, email: str) -> Optional[str]:
        """Return the user id for a given email address.

        :param email: Email to search for.
        :return: The user_id if found, None otherwise.
        """
        parameters = {"email": email}

        try:
            records = self.neo4jDriver.execute_read(
                CypherQueries.FIND_USER_BY_EMAIL,
                parameters
            )

            if len(records) > 1:
                logging.error(f"Database error: Multiple users found for email [{email}]!")

            return records[0]["user_id"] if records else None
        except Exception as e:
            logging.error(f"Error finding user by email: {email}, error: {e}")

        return None

    def get_user_password_hash(self, user_id: str) -> Optional[str]:
        """Return the hashed password for a given user id.

        :param user_id: The unique identifier for the user.
        :return: The hashed password if found, None otherwise.
        """
        parameters = {"user_id": user_id}

        try:
            records = self.neo4jDriver.execute_read(
                CypherQueries.GET_USER_PASSWORD_HASH,
                parameters
            )

            if len(records) > 1:
                logging.error(f"Database error: Multiple password hashes found for user [{user_id}]!")

            return records[0]["password_hash"] if records else None
        except Exception as e:
            logging.error(f"Error retrieving password hash for user: {user_id}, error: {e}")

        return None

    # Messages Management

    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a message by its id.

        :param message_id: ID of the message.
        :return: A dictionary with message details if found, None otherwise.
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": message_id,
        }

        try:
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
        except Exception as e:
            logging.error(f"Error retrieving message ID: {message_id}, error: {e}")

        return None

    def create_user_prompt_node(self, category: str, user_prompt: str, llm_response: str) -> str:
        """Saves a user prompt and response in the database.

        :param category: Category of the user prompt.
        :param user_prompt: The user prompt text.
        :param llm_response: The response from the LLM.
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

        try:
            user_prompt_id = self.neo4jDriver.execute_write(
                CypherQueries.POPULATE_USER_PROMPT_NODE,
                parameters,
                "user_prompt_id"
            )

            self.create_file_nodes_for_user_prompt(user_prompt_id, category)

            logging.info(f"User prompt node created with ID: {user_prompt_id}")
            return category
        except Exception as e:
            logging.error(f"Error creating user prompt node: {e}")
            return None

    def get_messages_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Retrieve messages linked to a specific category.

        :param category_name: The category to retrieve messages for.
        :return: A list of messages related to that category.
        """
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

        try:
            records = self.neo4jDriver.execute_read(CypherQueries.GET_MESSAGES, parameters)
            return [
                {"id": record["id"],
                 "prompt": record["prompt"],
                 "response": record["response"],
                 "time": record["time"]} for record in records
            ]
        except Exception as e:
            logging.error(f"Error retrieving messages by category: {category_name}, error: {e}")

        return []

    def delete_message_by_id(self, message_id: str) -> None:
        """Deletes a message by its ID.

        :param message_id: ID of the message to delete.
        """
        parameters = {
            "user_id": get_user_context(),
            "message_id": message_id,
        }

        try:
            self.neo4jDriver.execute_delete(CypherQueries.DELETE_MESSAGE_AND_POSSIBLY_CATEGORY, parameters)
            logging.info(f"User prompt node {message_id} deleted")
        except Exception as e:
            logging.error(f"Error deleting message ID: {message_id}, error: {e}")

    # Categories Management

    def create_category(self, category_name: str) -> None:
        """Creates a new category.

        :param category_name: Name of the category to create.
        """
        category_id = str(shortuuid.uuid())
        logging.info(f"Creating new category [{category_id}]: {category_name}")

        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name.lower(),
            "category_id": category_id
        }

        try:
            self.neo4jDriver.execute_write(
                CypherQueries.CREATE_CATEGORY,
                parameters
            )
        except Exception as e:
            logging.error(f"Error creating category: {category_name}, error: {e}")

    def get_category_id(self, category_name: str) -> Optional[str]:
        """Retrieve the ID of a category by its name.

        :param category_name: Name of the category.
        :return: The ID of the category if found, None otherwise.
        """
        parameters = {"category_name": category_name}

        try:
            records = self.neo4jDriver.execute_read(CypherQueries.GET_CATEGORY_ID, parameters)
            category_id = records[0]["category_id"] if records else None

            logging.info(f"Category ID for {category_name}: {category_id}")
            return category_id
        except Exception as e:
            logging.error(f"Error retrieving category ID: {category_name}, error: {e}")

        return None

    def list_categories(self) -> List[str]:
        """Lists all unique categories associated with the user.

        :return: A list of category names.
        """
        parameters = {
            "user_id": get_user_context()
        }

        try:
            result = self.neo4jDriver.execute_read(CypherQueries.LIST_CATEGORIES, parameters)
            return [record["category_name"] for record in result]  # Safe access with default values
        except Exception as e:
            logging.error(f"Error listing categories, error: {e}")

        return []

    def create_file_nodes_for_user_prompt(self, user_prompt_id: str, category: str) -> None:
        """Creates file nodes associated with the user prompt.

        :param user_prompt_id: The ID of the user prompt.
        :param category: The category of the prompt.
        """
        file_names = StorageMethodology.select().list_staged_files()

        for file_name in file_names:
            self.create_file_node(user_prompt_id, category, file_name)

    def create_file_node(self, user_prompt_id: str, category: str, file_path: str) -> None:
        """Creates a file node in the database representing the file content.

        :param user_prompt_id: ID of the associated user prompt.
        :param category: Category of the file.
        :param file_path: Path to the file.
        """
        try:
            time = int(datetime.now().timestamp())
            file_name = os.path.basename(file_path)

            content = StorageMethodology.select().read_file(file_path)
            from AiOrchestration.AiOrchestrator import AiOrchestrator
            executor = AiOrchestration()

            # Summarizes previous content if it exists when writing files
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

            logging.info(
                f"Creating file node: {category}/{file_name} against prompt [{user_prompt_id}]\nSummary: {summary}")
            self.neo4jDriver.execute_write(CypherQueries.CREATE_FILE_NODE, parameters)
        except Exception as e:
            logging.exception(f"Failed to save file node, error: {e}")

    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a file by its ID.

        :param file_id: ID of the file.
        :return: The file record if found, None otherwise.
        """
        parameters = {"file_id": file_id}

        try:
            records = self.neo4jDriver.execute_read(CypherQueries.GET_FILE_BY_ID, parameters)

            if records:
                return records[0]
        except Exception as e:
            logging.error(f"Error retrieving file by ID: {file_id}, error: {e}")

        return None

    def get_files_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Retrieve all files associated with a specified category.

        :param category_name: Name of the category.
        :return: A list of files related to that category.
        """
        parameters = {
            "user_id": get_user_context(),
            "category_name": category_name
        }

        try:
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
        except Exception as e:
            logging.error(f"Error retrieving files by category: {category_name}, error: {e}")

        return []

    def delete_file_by_id(self, file_id: int) -> None:
        """Deletes a specific file by its ID.

        :param file_id: ID of the file to be deleted.
        """
        parameters = {
            "user_id": get_user_context(),
            "file_id": file_id,
        }

        try:
            self.neo4jDriver.execute_delete(CypherQueries.DELETE_FILE_BY_ID, parameters)
            logging.info(f"File with ID {file_id} deleted")
        except Exception as e:
            logging.error(f"Error deleting file by ID: {file_id}, error: {e}")

    # User Topics Management

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
            except Exception as e:
                logging.error(f"Error creating user topic node: {term}, error: {e}")

    def search_for_user_topic_content(self, term: str, synonyms: Optional[List[str]] = None) -> Optional[
        Dict[str, Any]]:
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

        try:
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
        except Exception as e:
            logging.error(f"Error searching for user topic content: {term}, error: {e}")

        return None

    def list_user_topics(self) -> Optional[List[str]]:
        """Lists all user topics.

        :return: A list of user topic names if found, None otherwise.
        """
        parameters = {
            "user_id": get_user_context()
        }

        try:
            records = self.neo4jDriver.execute_read(
                CypherQueries.SEARCH_FOR_ALL_USER_TOPICS,
                parameters
            )
            if records:
                names = [record['name'] for record in records]
                return names
        except Exception as e:
            logging.error(f"Error listing user topics, error: {e}")

        return None

    # Pricing Methods

    def get_user_balance(self) -> Optional[float]:
        """Returns the current user balance.

        :return: The user balance if found, None otherwise.
        """
        parameters = {"user_id": get_user_context()}

        try:
            records = self.neo4jDriver.execute_read(
                CypherQueries.GET_USER_BALANCE,
                parameters
            )
            if len(records) > 1:
                logging.error(f"Database error: Multiple records found for user ID: {get_user_context()}!")
            return records[0]["balance"] if records else None
        except Exception as e:
            logging.error(f"Error retrieving user balance, error: {e}")

        return None

    def deduct_from_user_balance(self, amount: float) -> None:
        """Deducts a specific amount from the user's balance.

        :param amount: The amount to deduct (should be a positive value).
        """
        if amount <= 0:
            logging.error("Deduction amount must be positive.")
            return

        self.update_user_balance(-amount)

    def update_user_balance(self, amount: float) -> None:
        """Updates the user's balance by the specified amount.

        :param amount: A positive value to add to the user's balance.
        """
        parameters = {
            "user_id": get_user_context(),
            "sum": amount
        }

        try:
            self.neo4jDriver.execute_write(
                CypherQueries.UPDATE_USER_BALANCE,
                parameters
            )
            logging.info(f"User balance updated by: {amount}")
        except Exception as e:
            logging.error(f"Error updating user balance, error: {e}")

    def create_receipt(self, input_costs: float, output_costs: float, mode: str) -> None:
        """Creates a transaction receipt for the user.

        :param input_costs: The input costs incurred.
        :param output_costs: The output costs incurred.
        :param mode: The transaction mode.
        """
        logging.info(
            f"Logging receipt: {input_costs}, {output_costs}, {mode}, user ID: {get_user_context()}, message ID: {get_message_context()}")

        parameters = {
            "user_id": get_user_context(),
            "message_id": get_message_context(),
            "input_costs": input_costs,
            "output_costs": output_costs,
            "mode": mode
        }

        try:
            self.neo4jDriver.execute_write(
                CypherQueries.CREATE_RECEIPT,
                parameters
            )
            logging.info("Receipt created successfully.")
        except Exception as e:
            logging.error(f"Error creating receipt, error: {e}")


```

## Neo4jDriver.py

```python

```


## Pricing.py

```python
import logging

from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities import Globals


class Pricing:
    """
    Pricing class responsible for managing user balances and session costs.

    This class provides methods to retrieve user balance, top up balances, and get session costs.
    """

    @staticmethod
    def get_user_balance() -> float:
        """Retrieves the current user balance.

        :return: The current user balance.
        """
        return NodeDB().get_user_balance()

    @staticmethod
    def top_up_user_balance(amount: float) -> dict:
        """Tops up the user's balance by a specified amount.

        :param amount: The amount to add to the user's balance (must be positive).
        :return: A dictionary containing the status of the operation.
        :raises ValueError: If the amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Amount to top up must be greater than zero.")

        try:
            NodeDB().update_user_balance(amount)
            return {
                "status_code": 200,
                "message": f"User balance successfully topped up by ${amount:.2f}."
            }
        except Exception as e:
            logging.error(f"Failed to update user balance: {str(e)}", exc_info=True)
            return {
                "status_code": 500,
                "message": f"Failed to update user balance: {str(e)}"
            }

    @staticmethod
    def get_session_cost() -> float:
        """Retrieves the current session cost incurred by the user.

        :return: The session cost since deployment.
        """
        return Globals.current_request_cost

```

## EncylopediaManagement.py
```python

import logging
import os

from Data.EncyclopediaManagementInterface import EncyclopediaManagementInterface
from Data.WikipediaApi import search_wikipedia_api

class EncyclopediaManagement(EncyclopediaManagementInterface):
    """
    **EncyclopediaManagement**: A class for managing encyclopedia entries, enabling retrieval,
    updating, and organization of knowledge.

    This class implements a singleton pattern to ensure that only a single instance holds the cache in memory.
    """

    ENCYCLOPEDIA_NAME = "Encyclopedia"
    instructions = (
        "For the given prompt, return an array of concepts that would help answer this prompt. "
        "The term should be simple, e.g., the actual word of the concept. You can use "
        "the 'specifics' field if there is a particular aspect you would prefer to explore."
    )

    _instance = None

    def __new__(cls) -> "EncyclopediaManagement":
        """Create a singleton instance of EncyclopediaManagement."""
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the EncyclopediaManagement instance, setting paths for the encyclopedia 
        data files and loading the initial data.
        """
        super().__init__()
        # Set paths for both the encyclopedia and the redirects
        self.encyclopedia_path = os.path.join(self.data_path, f"{self.ENCYCLOPEDIA_NAME}.yaml")
        self.redirect_encyclopedia_path = os.path.join(self.data_path, f"{self.ENCYCLOPEDIA_NAME}Redirects.csv")
        self.load_encyclopedia_data()

    def fetch_term_and_update(self, term_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        This method retrieves the specified term's data from the Wikipedia API and refreshes the local encyclopedia
        cache to reflect the most current information. If any exception occurs during the process, it logs the error.

        :param term_name: The name of the term to fetch from Wikipedia.
        :return: A status indicating whether the fetching and updating were successful.
        """
        try:
            search_wikipedia_api(term_name, self.ENCYCLOPEDIA_NAME)
            self.load_encyclopedia_data()
            logging.info(f"Successfully fetched and updated term '{term_name}' in the encyclopedia.")
            return True
        except Exception as e:
            logging.exception(f"Error while accessing '{self.ENCYCLOPEDIA_NAME}' for term '{term_name}'", exc_info=e)
            return False


if __name__ == '__main__':
    encyclopedia_management = EncyclopediaManagement()
    result = encyclopedia_management.search_encyclopedia(["Can you talk about 'code reuse'?"])
    print(result)

```

## EncyclopediaManagementInterface.py


```python
import logging
import os
import pandas as pd
import yaml

from typing import List, Dict, Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Personas.PersonaSpecification.PersonaConstants import SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
from Utilities.Constants import DEFAULT_ENCODING
from Utilities.Decorators import handle_errors


class EncyclopediaManagementInterface:
    """
    **EncyclopediaManagementInterface**: Manages encyclopedia data files and provides search and retrieval capabilities.

    This class facilitates loading encyclopedia entries and redirects, searching for terms,
    and summarizing information relevant to user queries.
    """

    ENCYCLOPEDIA_EXT = ".yaml"
    REDIRECTS_EXT = "Redirects.csv"
    ENCYCLOPEDIA_NAME = "To Define"
    instructions = "To Define"

    _instance: Optional['EncyclopediaManagementInterface'] = None

    def __new__(cls) -> 'EncyclopediaManagementInterface':
        """Implements the singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(EncyclopediaManagementInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initializes the EncyclopediaManagementInterface."""
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.encyclopedia: Dict[str, str] = {}
            self.redirects: Dict[str, str] = {}

            self.encyclopedia_path = "To Define"
            self.redirect_encyclopedia_path = "To Define"

            self.data_path = os.path.join(os.path.dirname(__file__), 'DataStores')
            self.initialized = True

    def load_encyclopedia_data(self) -> None:
        """Load encyclopedia and redirect data from the specified files."""
        try:
            self.encyclopedia = self._load_yaml_file(self.encyclopedia_path)
            self.redirects = self._load_redirects(self.redirect_encyclopedia_path)
            logging.info("Encyclopedia and redirects loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading encyclopedia data: {e}", exc_info=e)

    @staticmethod
    @handle_errors(raise_errors=True)
    def _load_yaml_file(filepath: str) -> Dict[str, str]:
        """Load a YAML file and return its content as a dictionary.

        :param filepath: Path to the YAML file to load.
        :return: Dictionary containing the file contents.
        """
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as file:
            return yaml.safe_load(file) or {}

    @staticmethod
    @handle_errors(raise_errors=True)
    def _load_redirects(filepath: str) -> Dict[str, str]:
        """Load redirect terms from a CSV file and return them as a dictionary.

        :param filepath: Path to the CSV file containing redirects.
        :return: Dictionary mapping redirect terms to target terms.
        """
        redirects_df = pd.read_csv(filepath, header=None, names=['redirect_term', 'target_term'])
        return redirects_df.set_index('redirect_term')['target_term'].to_dict()

    @handle_errors(raise_errors=True)
    def search_encyclopedia(self, user_messages: List[str]) -> str:
        """Searches the encyclopedia for terms derived from user messages.

        :param user_messages: List of user input messages containing the terms.
        :return: A string representation of the additional context found.
        """
        executor = AiOrchestrator()
        output = executor.execute_function(
            [self.instructions],
            user_messages,
            SEARCH_ENCYCLOPEDIA_FUNCTION_SCHEMA
        )
        terms = output['terms']
        logging.info(f"Terms to search for in {self.ENCYCLOPEDIA_NAME}: {terms}")

        return self.extract_terms_from_encyclopedia(terms)

    def extract_terms_from_encyclopedia(self, terms: List[Dict[str, str]]) -> str:
        """Search for a set of terms in the encyclopedia and return additional context.

        :param terms: The terms to check in the encyclopedia.
        :return: A string representation of additional context extracted.
        """
        additional_context = []

        for term in terms:
            try:
                term_name = term['term'].lower().strip()
                user_topics = nodeDB().list_user_topics()

                executor = AiOrchestrator()
                selected_topic_raw = executor.execute(
                    ["Given the list of topics I gave you, just return the most appropriate from the list"],
                    [term.get("term") + " : " + term.get("specifics"), str(user_topics)]
                )
                selected_topic = selected_topic_raw.strip("'")

                content = nodeDB().search_for_user_topic_content(selected_topic)
                if content:
                    additional_context.append(content)

            except Exception as e:
                logging.exception(f"Error while trying to access {self.ENCYCLOPEDIA_NAME}: {term_name}", exc_info=e)

        return str(additional_context)

    def selectively_process_entry(self, term_name: str, specifics: str) -> str:
        """Processes a specific encyclopedia entry to summarize information.

        :param term_name: The term to search for in encyclopedia data.
        :param specifics: The specifics about what to explore regarding the term.
        :return: A summarized version of the encyclopedia file content.
        """
        entry_dict = self.encyclopedia.get(term_name)
        executor = AiOrchestrator()
        output = executor.execute(
            [
                "Summarize the following information while retaining essential details."
            ],
            [
                term_name + ": " + specifics,
                str(entry_dict)
            ]
        )

        return output

    def fetch_term_and_update(self, term_name: str) -> bool:
        """Fetches the term from Wikipedia and updates the encyclopedia.

        :param term_name: The name of the term to fetch from Wikipedia.
        :return: A status indicating whether the fetching and updating were successful.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


if __name__ == '__main__':
    pass

```

## EncylopediaManagement.py

```python

```

## CypherQueries.py

```python

```

## Configuration.py

```python
import logging
import os
from typing import Mapping, Dict, Any

from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context


# REVIEW: Missunderstanding, my system is designed to already supply folder paths, it just needs the file names
USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'UserConfigs')
DEFAULT_CONFIG_FILE = os.path.join(USER_CONFIG_PATH, "Config.yaml")


class Configuration:
    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deeply merges dict2 into dict1. dict2 takes precedence over dict1.

        :param dict1: The base dictionary.
        :param dict2: The dictionary to merge over `dict1`.
        :returns: The merged dictionary.
        """
        for key, value in dict2.items():
            if isinstance(value, Mapping) and key in dict1 and isinstance(dict1[key], Mapping):
                Configuration.deep_merge(dict1[key], value)
            else:
                dict1[key] = value
        return dict1

    @staticmethod
    def load_config(yaml_file: str = DEFAULT_CONFIG_FILE) -> Dict[str, Any]:
        """
        Loads the configuration from the baseline YAML file then merges the user's config on top,
        extracting the combined values.

        :param yaml_file: The path to the YAML file
        :returns: A dictionary containing the extracted configuration values
        :raises FileNotFoundError: If the specified YAML file does not exist.
        """
        try:
            config = StorageMethodology.select().load_yaml(yaml_file)
            user_config_path = os.path.join(USER_CONFIG_PATH, f"{get_user_context()}.yaml")
            user_config = StorageMethodology.select().load_yaml(user_config_path)

            # Merge user_config into config
            merged_config = Configuration.deep_merge(config, user_config)

            return merged_config
        except FileNotFoundError as e:
            logging.error(f"Configuration file not found: {e}")
            raise

    @staticmethod
    def update_config_field(field_path: str, value: Any) -> None:
        """
        Updates a particular field in the user's YAML configuration file.
        For first-time changes, a new user config file will be created automatically.

        :param field_path: The dot-separated path to the field to update (e.g., 'interface.dark_mode').
        :param value: The value to set for the specified field.
        :raises FileNotFoundError: If the user configuration file does not exist.
        :raises Exception: If there are issues while saving the configuration.
        """
        try:
            file_storage = StorageMethodology.select()
            user_config_path = os.path.join(USER_CONFIG_PATH, f"{get_user_context()}.yaml")

            config = file_storage.load_yaml(user_config_path)

            # Navigate to the specified field and update the value
            keys = field_path.split('.')
            current = config
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = value

            # Save the updated configuration back to the YAML file
            file_storage.save_yaml(user_config_path, config)
        except FileNotFoundError as e:
            logging.error(f"User configuration file not found: {e}")
            raise
        except Exception as e:
            logging.error(f"Error while updating the configuration field: {e}")
            raise


if __name__ == '__main__':
    # Example usage
    config = Configuration()
    config_items = config.load_config()
    print(config_items)
    print(config_items.get('documentation', {}).get('style', 'N/A'))  # Output: reStructuredText or 'N/A'
    print(config_items.get('writing', 'N/A'))  # Output: Configuration for 'writing' or 'N/A'

```

## CategoryManagement.py

sanitize_category_name is legitmately a great suggestion

```python
import logging
import os
import re
from typing import Optional

from AiOrchestration.AiOrchestrator import AiOrchestrator
from Data.Configuration import Configuration
from Data.Files.FileManagement import FileManagement
from Data.NodeDatabaseManagement import NodeDatabaseManagement as nodeDB
from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context


class CategoryManagement:
    """
    Manages the automatic categorisation of uploaded files and files created by the system.

    This class provides methods to categorize user input and manage the categories 
    within a database. It uses an orchestrator to determine the appropriate category 
    based on user input and system responses.
    """
    
    _instance = None

    def __new__(cls):
        """Implements the singleton pattern to ensure only one instance of CategoryManagement exists."""
        if cls._instance is None:
            cls._instance = super(CategoryManagement, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the CategoryManagement instance, setting up the AI orchestrator."""
        self.executor = AiOrchestrator()

    @staticmethod
    def sanitize_category_name(category: str) -> str:
        """
        Sanitize the category name to remove invalid characters like '/'.

        :param category: The category name to be sanitized.
        :return: A sanitized category name.
        """
        return category.replace('/', '_')  # Replace '/' to avoid routing issues

    @staticmethod
    def categorize_prompt_input(user_prompt: str, llm_response: Optional[str] = None, creating: bool = True) -> str:
        """
        Categorizes the user input based on prompt and optional response using the AI orchestrator.

        :param user_prompt: The user's input prompt string.
        :param llm_response: Optional AI response for additional context.
        :param creating: Flag indicating if a new category should be created.
        :return: Name of the selected category.
        """
        categories = nodeDB().list_categories()
        config = Configuration.load_config()

        user_categorization_instructions = config.get('systemMessages', {}).get(
            "categorisationMessage",
            "Given the following prompt-response pair, think through step by step and explain your reasoning."
        )

        if llm_response:
            categorization_input = (
                f"<user prompt>{user_prompt}</user prompt>\n"
                f"<response>{llm_response}</response>"
            )
        else:
            categorization_input = f"<user prompt>{user_prompt}</user prompt>\n"
        
        categorization_instructions = (
            f"LIGHTLY suggested existing categories, you DON'T need to follow: {categories}. "
            f"{user_categorization_instructions} "
            "Categorize the data with the most suitable single-word answer. "
            "Write it as <result=\"(your_selection)\""
        )

        category_reasoning = CategoryManagement().executor.execute(
            [categorization_instructions],
            [categorization_input]
        )
        logging.info(f"Category Reasoning: {category_reasoning}")
        category = CategoryManagement.extract_example_text(category_reasoning)

        return CategoryManagement.possibly_create_category(category)

    @staticmethod
    def possibly_create_category(category: str) -> str:
        """
        Creates a category in the database if it does not already exist.

        :param category: The category to potentially add to the node database.
        :return: The existing or newly created category.
        """
        sanitized_category = CategoryManagement.sanitize_category_name(category)
        categories = nodeDB().list_categories()

        if sanitized_category not in categories:
            nodeDB().create_category(sanitized_category)

        return sanitized_category

    @staticmethod
    def extract_example_text(input_string: str) -> Optional[str]:
        """
        Extracts the text contained within the result element.

        :param input_string: The string containing the result element.
        :return: The text inside the result element, or None if not found.
        """
        match = re.search(r'<result="([^"]+)">', input_string)
        if match:
            return match.group(1)

        logging.warning("Failed to categorize input string.")
        return None

    @staticmethod
    def stage_files(category: Optional[str] = None) -> None:
        """
        Stages files into a specific category based on user prompt.

        Retrieves files from the staging area, summarizes them, 
        and categorizes according to their content using an AI orchestrator.

        :param category: The category to categorize staged files. If None, a category will be generated.
        """
        files = StorageMethodology.select().list_staged_files()
        logging.info(f"Staged files: {files}")

        category_id = CategoryManagement._get_or_create_category_id(category)
        
        if not files:
            logging.info("No files to stage.")
            return

        try:
            for file in files:
                staged_file_path = os.path.join(file)
                new_file_path = os.path.join(str(category_id), os.path.basename(file))
                StorageMethodology.select().move_file(staged_file_path, new_file_path)
                logging.info(f"Moved file {file} to {new_file_path}")
        except Exception as e:
            logging.exception(f"ERROR: Failed to move files: {files} to folder: {category_id}. Reason: {str(e)}")

    @staticmethod
    def _get_or_create_category_id(category_name: str) -> Optional[str]:
        """Retrieves or creates a category ID for the specified category name.

        :param category_name: The name of the category.
        :return: The category ID if found; otherwise None.
        """
        sanitized_category_name = CategoryManagement.sanitize_category_name(category_name)
        category_id = nodeDB().get_category_id(sanitized_category_name)

        if category_id is None:
            CategoryManagement._add_new_category(sanitized_category_name)

        logging.info(f"Id found or created for category [{category_id}] - {sanitized_category_name}")

        return category_id

    @staticmethod
    def _add_new_category(category_id: str) -> None:
        """
        Creates a folder to store files against a given category.

        :param category_id: The new folder category ID to create.
        """
        new_directory = os.path.join(FileManagement.file_data_directory, category_id)
        os.makedirs(new_directory, exist_ok=True)  

    @staticmethod
    def determine_category(user_prompt: str, tag_category: Optional[str] = None) -> str:
        """
        Determines the category for the user prompt.

        :param user_prompt: The user's input prompt.
        :param tag_category: Optional tag category from the front end.
        :return: The determined category.
        """
        if tag_category is None:
            category = CategoryManagement.categorize_prompt_input(user_prompt)
            logging.info(f"Prompt categorized as: {category}")
            return category

        return tag_category


if __name__ == '__main__':
    CategoryManagement.stage_files("Put this file in Notes please")

```
