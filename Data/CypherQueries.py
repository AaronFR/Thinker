
CREATE_CATEGORY = """
MERGE (user:USER)
WITH user
MERGE (category:CATEGORY {name: $category_name})
ON CREATE SET category.id = $category_id
MERGE (user)-[:HAS_CATEGORY]->(category)
RETURN id(category) AS category_id
"""

CREATE_USER_PROMPT_NODES = """
MERGE (user:USER)
WITH user
MATCH (category:CATEGORY {name: $category})<-[:HAS_CATEGORY]-(user)
CREATE (user_prompt:USER_PROMPT {prompt: $prompt, response: $response, time: $time})
MERGE (user)-[:USES]->(category)
MERGE (user_prompt)-[:BELONGS_TO]->(category)
RETURN id(user_prompt) AS user_prompt_id
"""

CREATE_FILE_NODE = """
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

# Messages
GET_MESSAGES = """
MATCH (user:USER)-[:USES]->(category:CATEGORY {name: $category_name})
    <-[:BELONGS_TO]-(user_prompt:USER_PROMPT)
RETURN id(user_prompt) AS id, user_prompt.prompt AS prompt, user_prompt.response AS response, user_prompt.time AS time
ORDER by user_prompt.time DESC
"""

DELETE_MESSAGE_AND_POSSIBLY_CATEGORY = """
MATCH (message:USER_PROMPT)-[:BELONGS_TO]->(category:CATEGORY)
WHERE id(message) = $message_id
DETACH DELETE message
WITH category
OPTIONAL MATCH (category)<-[:BELONGS_TO]-(remaining_messages:USER_PROMPT)
WITH category, count(remaining_messages) AS remaining_count
WHERE remaining_count = 0
DETACH DELETE category
"""

# Categories
GET_CATEGORY_ID = """
MATCH (category:CATEGORY {name: $category_name})
RETURN category.id AS category_id
"""

LIST_CATEGORIES = """
MATCH (user:USER)-[:USES]->(category:CATEGORY)
RETURN DISTINCT category.name as category_name
ORDER by category_name
"""

LIST_CATEGORIES_WITH_FILES = """
MATCH (user:USER)-[:USES]->(category:CATEGORY)--(file:FILE)
RETURN DISTINCT category.name as category_name
ORDER by category_name
"""

# Files
GET_FILE_BY_ID = """
MATCH (category:CATEGORY)--(file:FILE)
WHERE id(file) = $file_id
RETURN id(file) AS id, category.id AS category, file.name AS name, file.summary AS summary, file.structure AS structure, file.time AS time
ORDER by file.time DESC
"""

GET_FILES_FOR_CATEGORY = """
MATCH (user:USER)-[:USES]->(category:CATEGORY {name: $category_name})
    <-[:BELONGS_TO]-(file:FILE)
RETURN id(file) AS id, category.id AS category_id, file.name AS name, file.summary AS summary, file.structure AS structure, file.time AS time
ORDER by file.time DESC
"""

DELETE_FILE_BY_ID = """
MATCH (file:FILE)-[:BELONGS_TO]->(category:CATEGORY)
WHERE id(file) = $file_id
DETACH DELETE file
"""