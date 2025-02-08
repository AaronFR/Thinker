# PRICING (!)

FAILED_TO_UPDATE_USER_BALANCE = "FAILED TO UPDATE USER BALANCE!"


def failed_to_retrieve_user_balance(user_id: str):
    return f"Error retrieving balance for user_id {user_id}"


# Schema Errors

FUNCTION_SCHEMA_EMPTY = "Function schema cannot be empty."


# 3rd Party Errors

AI_RESOURCE_FAILURE = "Failed to get response from AI resource"
SERVER_FAILURE_OPEN_AI_API = "OpenAI API Server Failure"
SERVER_FAILURE_GEMINI_API = "Gemini Server Failure"
NO_RESPONSE_OPEN_AI_API = "OpenAI API returned no response."
NO_RESPONSE_GEMINI_API = "Gemini API returned no response."
OPEN_AI_FLAGGED_REQUEST_INAPPROPRIATE = "OpenAi ChatGpt Flagged user request as Inappropriate"

# Route Failures

FAILURE_TO_SELECT_PERSONA = "Failed to select persona"
FAILURE_TO_SELECT_WORKFLOW = "Failed to select workflow"
FAILURE_TO_AUTO_ENGINEER_PROMPT = "Failed to automatically engineer prompt"
FAILURE_TO_QUESTION_PROMPT = "Failed to generate questions for message"

FAILURE_TO_LOGIN = "Failed to login"
FAILURE_TO_VALIDATE_SESSION = "Error validating token"
FAILURE_TO_LOGOUT_SESSION = "Failed to log the user out of the current session"

FAILURE_TO_GET_USER_INFO = "Failed to fetch user information."

FAILURE_TO_STREAM = "Failed to stream"

# File Failures


def file_not_found(file_address: str):
    return f"FILE NOT FOUND: {file_address}"


def file_not_loaded(file_address: str):
    return f"FAILED TO LOAD {file_address}"


def file_not_deleted(file_id: str):
    return f"Failed to delete file {file_id}"


def user_staging_area_not_found(staging_directory: str):
    return f"The directory {staging_directory} does not exist."


FAILURE_TO_READ_FILE = "An unexpected error occurred while reading the file."
FAILURE_TO_LIST_STAGED_FILES = "An error occurred while listing staged files."


def failure_to_suggest_colour_for_category(category_name: str):
    return f"AI color assignment failed for category '{category_name}'"


def failure_to_create_description_for_category(category_name: str):
    return f"AI color assignment failed for category '{category_name}'"


def cannot_read_image_file(full_address: str):
    return f"CANNOT READ IMAGE FILE: {full_address}"


# Data


def failed_to_create_user_topic(topic: str):
    return f"Error creating user topic node: {topic}"


# Persona System

FAILURE_TO_REVIEW_RELEVANT_HISTORY = "Failed to Retrieve relevant history"

# GENERIC

NOT_IMPLEMENTED_IN_INTERFACE = "This method should be overridden by subclasses"


def error_in_function(function_name: str, exception: Exception):
    return f"Error in {function_name}:\n{exception}"


# Workflows

def failure_to_process_file_in_workflow(file_ref: str):
    return f"Error processing file '{file_ref}'"


def failure_to_process_individual_page_iteration(iteration: int):
    return f"Error processing page {iteration}"





