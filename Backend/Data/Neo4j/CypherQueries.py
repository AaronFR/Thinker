"""
CypherQueries.py

This module contains Cypher queries used for interacting with the Neo4j Graph Database.

Constraints:
CREATE CONSTRAINT FOR (user:USER) REQUIRE user.id IS UNIQUE;
CREATE CONSTRAINT FOR (category:CATEGORY) REQUIRE category.id IS UNIQUE;
CREATE CONSTRAINT FOR (s:SYSTEM) REQUIRE s.id IS UNIQUE;
"""
from typing import List

# ToDo: include secure user match e.g MATCH (user:USER {id: $user_id})
#  That way it reduces the odds of forgetting to add a user check

# Auth

FIND_USER_BY_EMAIL = """
MATCH (user:USER)
WHERE user.email = $email
RETURN user.id AS user_id;
"""

GET_USER_PASSWORD_HASH = """
MATCH (user:USER)
WHERE user.id = $user_id
RETURN user.password_hash AS password_hash;
"""

CREATE_USER = """
MERGE (user:USER {id: $user_id})
ON CREATE SET user.email = $email, user.password_hash = $password_hash, user.balance = 0
RETURN user.id;
"""

MARK_VERIFIED = """
MATCH (user:USER)
WHERE user.email = $email
SET user.verified = true
RETURN user.verified AS verified_status;
"""


# CREATE

CREATE_CATEGORY = """
MATCH (user:USER {id: $user_id})
WITH user
MERGE (category:CATEGORY {name: $category_name, description: $category_description, colour: $colour})
ON CREATE SET category.id = $category_id
MERGE (user)-[:HAS_CATEGORY]->(category)
RETURN category.id AS category_id;
"""

CREATE_USER_PROMPT_BLANK_AND_CATEGORY = """
MATCH (user:USER {id: $user_id})
WITH user
MERGE (category:CATEGORY {name: $category_name, description: $category_description, colour: $colour})
ON CREATE SET category.id = $category_id
MERGE (user)-[:HAS_CATEGORY]->(category)
CREATE (user_prompt:USER_PROMPT {id: $message_id}) 
MERGE (user_prompt)-[:BELONGS_TO]->(category) 
RETURN category.id AS category_id;
"""

CREATE_USER_TOPIC = """
MATCH (user:USER {{id: $user_id}})
WITH user
MERGE (user_topic:USER_TOPIC {{_name_: $node_name}})
SET user_topic.{parameter} = $content
MERGE (user_topic)-[:RELATES_TO]->(user)
RETURN id(user_topic) AS user_topic_id;
"""


def format_create_user_topic_query(parameter: str) -> str:
    """Formats the query to create a user topic with the specified parameter."""
    return CREATE_USER_TOPIC.format(parameter=parameter)


SEARCH_FOR_USER_TOPIC = """
MATCH (user:USER {id: $user_id})
WITH user
MATCH (user_topic:USER_TOPIC {_name_: $node_name})
RETURN properties(user_topic) AS all_properties;
"""

# newest first
SEARCH_FOR_ALL_USER_TOPICS = """
MATCH (user:USER {id: $user_id})
WITH user
MATCH (user_topic:USER_TOPIC)
WITH user_topic
ORDER BY id(user_topic) DESC
RETURN user_topic._name_ AS name;
"""

CREATE_USER_PROMPT_NODE = """
MATCH (user:USER {id: $user_id})
WITH user
MATCH (category:CATEGORY {name: $category})<-[:HAS_CATEGORY]-(user)
CREATE (user_prompt:USER_PROMPT {id: $message_id})
MERGE (user)-[:HAS_CATEGORY]->(category)
MERGE (user_prompt)-[:BELONGS_TO]->(category)
RETURN user_prompt.id AS user_prompt_id;
"""

POPULATE_USER_PROMPT_NODE = """
MATCH (user:USER {id: $user_id})
WITH user
MATCH (category:CATEGORY {name: $category})<-[:HAS_CATEGORY]-(user)
MERGE (user_prompt:USER_PROMPT {id: $message_id})
SET user_prompt.prompt = $prompt, user_prompt.response = $response, user_prompt.time = $time
MERGE (user)-[:HAS_CATEGORY]->(category)
MERGE (user_prompt)-[:BELONGS_TO]->(category)
RETURN user_prompt.id AS user_prompt_id;
"""


"""
Summary:
Find the user and the category the file node belongs to
Check for any previous file node with that same name
    if a previous file exists merge over it and update the version number
Create a relationship to the user prompt node that created/update this file
Return the files Data
"""
CREATE_FILE_NODE = """
MATCH (user:USER {id: $user_id})
MATCH (user)--(category:CATEGORY {id: $category_id})
WITH user, category
OPTIONAL MATCH (user_prompt:USER_PROMPT {id: $user_prompt_id})
OPTIONAL MATCH (existingFile:FILE)-[:BELONGS_TO]->(category)
WHERE existingFile.name = $name
WITH existingFile, user_prompt, category
MERGE (newFile:FILE {name: $name})-[:BELONGS_TO]->(category)
SET newFile.version = COALESCE(existingFile.version, 0) + 1,
    newFile.id = $file_id,
    newFile.time = $time,
    newFile.size = $size,
    newFile.summary = $summary,
    newFile.structure = $structure
FOREACH (up IN CASE WHEN user_prompt IS NOT NULL THEN [user_prompt] ELSE [] END |
    CREATE (newFile)-[:ORIGINATES_FROM {version: newFile.version}]->(up)
)
RETURN newFile;
"""


# Messages

GET_MESSAGE = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)
    <-[:BELONGS_TO]-(user_prompt:USER_PROMPT {id: $message_id})
RETURN user_prompt.id AS id, user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time;
"""

GET_MESSAGES = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY {name: $category_name})
    <-[:BELONGS_TO]-(user_prompt:USER_PROMPT)
RETURN user_prompt.id AS id, user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time, user_prompt.cost as cost
ORDER BY user_prompt.time DESC;
"""

DELETE_MESSAGE_AND_POSSIBLY_CATEGORY = """
MATCH (message:USER_PROMPT)-[:BELONGS_TO]->(category:CATEGORY)<-[:HAS_CATEGORY]-(user:USER {id: $user_id})
WHERE message.id = $message_id
DETACH DELETE message
WITH category
OPTIONAL MATCH (category)<-[:BELONGS_TO]-(remaining_messages:USER_PROMPT)
WITH category, COUNT(remaining_messages) AS remaining_count
WHERE remaining_count = 0
DETACH DELETE category;
"""

# Categories

GET_CATEGORY_ID = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY {name: $category_name})
RETURN category.id AS category_id;
"""

LIST_CATEGORIES = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)
RETURN DISTINCT category.name AS category_name
ORDER BY category_name;
"""

LIST_CATEGORIES_BY_LATEST_MESSAGE= """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)
OPTIONAL MATCH (category)<-[:BELONGS_TO]-(message:USER_PROMPT)
RETURN DISTINCT category.name AS category_name, category.colour AS colour, category.description as description, max(message.time) AS latest_time
ORDER BY 
    CASE WHEN latest_time IS NULL THEN 1 ELSE 0 END, 
    latest_time DESC,
    category_name ASC;
"""

LIST_CATEGORIES_WITH_FILES = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)--(file:FILE)
RETURN DISTINCT category.name AS category_name
ORDER BY category_name;
"""

LIST_CATEGORIES_WITH_FILES_BY_LATEST_FILE = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)--(file:FILE)
OPTIONAL MATCH (category)<-[:BELONGS_TO]-(file:FILE)
RETURN DISTINCT category.name AS category_name, category.colour AS colour, max(file.time) AS latest_time
ORDER BY 
    CASE WHEN latest_time IS NULL THEN 1 ELSE 0 END, 
    latest_time DESC,
    category_name ASC;
"""

# Files

GET_FILE_BY_ID = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY)--(file:FILE)
WHERE file.id = $file_id
RETURN file.id AS id, category.id AS category, file.name AS name, file.summary AS summary, file.structure AS structure, file.time AS time, file.size as size
ORDER BY file.time DESC;
"""

GET_FILES_FOR_CATEGORY = """
MATCH (user:USER {id: $user_id})-[:HAS_CATEGORY]->(category:CATEGORY {name: $category_name})
    <-[:BELONGS_TO]-(file:FILE)
RETURN file.id AS id, category.id AS category_id, file.name AS name, file.summary AS summary, file.structure AS structure, file.time AS time, file.size as size
ORDER BY file.time DESC;
"""

DELETE_FILE_BY_ID = """
MATCH (file:FILE)-[:BELONGS_TO]->(category:CATEGORY)<-[:HAS_CATEGORY]-(user:USER)
WHERE file.id = $file_id AND user.id = $user_id
DETACH DELETE file;
"""

# Pricing

GET_USER_BALANCE = """
MATCH (user:USER {id: $user_id})
RETURN user.balance AS balance;
"""

GET_EARMARKED_SUM = """
MATCH (user:USER {id: $user_id})
RETURN user.earmarked AS earmarked_sum;
"""

"""
Note: an '$amount' is typically negative except for when paying into the system
'$earmarkedAmount' is positive
"""
UPDATE_USER_BALANCE = """
MATCH (user:USER {id: $user_id})
SET user.balance = user.balance + $amount + $earmarkedAmount,
    user.earmarked = user.earmarked - $earmarkedAmount;
"""

EARMARK_AGAINST_USER_BALANCE = """
MATCH (user:USER {id: $user_id})
SET user.balance = user.balance - $amount,
    user.earmarked = COALESCE(user.earmarked, 0) + $amount
RETURN user.earmarked as total_earmarked;
"""

# Will create the node if it doesn't already yet exist
EXPENSE_NODE = """
MERGE (n {id: $node_id})
SET n.cost = COALESCE(n.cost, 0) + $amount
RETURN n;
"""

EXPENSE_FUNCTIONALITY = """
MATCH (user:USER {id: $user_id})
SET user[$functionality] = COALESCE(user[$functionality], 0.0) + $amount
RETURN user[$functionality]
"""


def fetch_user_params_query(user_id: str, params: List[str]):
    """
    Define query to get
    """
    # Construct dynamic projection
    projection = ", ".join([f"user.{param} AS {param}" for param in params])

    return f"""
    MATCH (user:USER {{id: "{user_id}"}})
    RETURN {projection}
    """


# SYSTEM prompts

GET_SYSTEM_GEMINI_BALANCE = """
MATCH (system:SYSTEM)
RETURN system.gemini_balance AS gemini_balance;
"""

UPDATE_SYSTEM_GEMINI_BALANCE = """
MATCH (system:SYSTEM)
SET system.gemini_balance = system.gemini_balance + $amount;
"""

UPDATE_SYSTEM_OPEN_AI_BALANCE = """
MATCH (system:SYSTEM)
SET system.open_ai_balance = system.open_ai_balance + $amount;
"""


# Promotions


NEW_USER_PROMOTIONS_REMAINING = """
MATCH (system:SYSTEM)
RETURN system.new_user_promotions_remaining as new_user_promotions_remaining
"""

APPLY_NEW_USER_PROMOTION = """
WITH $email AS email
MATCH (user:USER {email: email})
WITH email, COUNT(user) AS userCount
WHERE userCount = 1
MATCH (system:SYSTEM)
WHERE system.new_user_promotions_remaining > 0
MATCH (user:USER {email: email})
WHERE user.new_user_promotion_applied IS NULL OR user.new_user_promotion_applied = false
SET system.new_user_promotions_remaining = system.new_user_promotions_remaining - 1,
    user.balance = user.balance + 1.0,
    user.new_user_promotion_applied = true
RETURN user.balance AS user_balance, system.new_user_promotions_remaining AS new_user_promotions_remaining
"""
