import logging
from typing import List


def plan_file_creation(initial_message: str, file_name: str) -> str:
    return (
        f"<user_prompt>{initial_message}</user_prompt>: To start with narrow your focus on "
        f"{file_name} and think through how to change or write it to fulfill the user's prompt to the highest standard,"
        "step by step. "
        "Discuss what we know, identify specifically what the user wants accomplished, goals and "
        f"sub-goals, and any existing flaws or defects WITHOUT writing any text or code for {file_name}. \n"
        "You are just writing up a plan of action instructing the LLM to follow how to rewrite or write the file "
        "in line with this plan and specifying that this plan is to be replaced with the actual functioning "
        "file."
    )


def plan_pages_to_write(page_count: int) -> str:
    return (
        "Provide a Markdown list of prompts to create a series of pages based on the following user message. "
        "Each prompt corresponds to one 'page'. Ensure that all prompts are clear, concise, and collectively "
        "provide valid and comprehensive instructions to fully satisfy the user's needs. If necessary, "
        "think through the problem outside of the list of prompts. "
        f"I expect {page_count} prompts. No more, no less."
    )


def write_file(file_name: str, purpose: str) -> str:
    return (
        f"Write/Rewrite {file_name} based on your previous plan of action for this particular file, "
        f"focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
        "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
        "Unless explicitly requested, the file's content must be preserved by default."
    )


def write_code_file(file_name: str, purpose: str) -> str:
    return (
        f"Write/Rewrite {file_name} based on your previous plan of action and the actual contents of "
        f"this particular file, focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
        "Making sure that the file imports as necessary, referencing the appropriate classes. "
        "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
        "Unless explicitly requested, the file's content must be preserved by default."
        "Finally, understand what you did or did not do, if you can see a file in your history that was they way they"
        "WERE, its YOUR job to change the file in line with the users prompt, not act like you've written code you "
        "haven't."
    )


def multiple_pages_summary_message(file_references: List[str], initial_message: str) -> str:
    return (
        f"Write a very quick summary indicating that each file in {file_references} has been processed "
        f"according to the initial user message: <user_message>{initial_message}</user_message>"
    )


DEFAULT_EXTRACT_SEARCH_TERMS_SYSTEM_MESSAGE = (
    "You are an assistant that extracts relevant search phrases/sentences from user prompts for internet searches.\n"
    "Search terms should be lengthy sentences and give contextual information"
)

PARSE_MEMORY_NODES_SYSTEM_MESSAGE = (
    "You are an assistant designed to intelligently navigate a node memory system to extract context "
    "based on provided node names.\n"
    "When a request is made, analyze the given list of context nodes and deduce which one likely contains the "
    "relevant information.\n"
    "You should prioritize the most specific and pertinent nodes related to the inquiry.\n"
    "For example, if asked for a user's name, consider the nodes provided and ascertain which one, "
    "such as 'personal', is most likely to contain this data.\n"
    "Focus on following succinct, logical conclusions based on the structural relationships of the nodes "
    "presented."
)


def extract_memory_node_terms_system_message(existing_nodes: List[str] = 'No Knowledge on user yet') -> str:
    return (
        "You are an assistant that helps store helpful information about the user to long term memory in a "
        "prescribed format."
        "This information is used as context in future prompts, so you prioritise ensuring the information is "
        "relevant to the user and correct. \n"
        "You prefer writing to one single meaningful topic node name instead of creating new but overly-similar "
        "nodes."
        "Identify and return an array of specific, concise items that describe context that can be inferred"
        " node_name and parameter should ideally be singular words; if not, must have underscores, not spaces. "
        "Format. fields in brackets are placeholders and should be filled, include the words parameter and content "
        "they are not to be replaced"
        "<(topic_name) parameter=\"(sub_topic_name)\" "
        "content=\"(the content you want to note on that sub_topic)\" />"
        "Required: (topic_name), (sub_topic_name), (content), all 3 must be included."
        "Don't actually write the ( brackets.\n"
        "Example format:\n"
        "<movies parameter=\"favorite\" content=\"Ikiru\" />"
        f"\n\nPRE-EXISTING NODES: {existing_nodes}"
    )

# Augmentation


AUTO_SELECT_WORKER_SYSTEM_MESSAGE = (
    "You are an assistant that selects an appropriate worker based on the user's prompt. "
    "Choose one of the following workers: 'coder' or 'writer'."
)

AUTO_SELECT_WORKFLOW_SYSTEM_MESSAGE = (
    "You are an assistant that selects the most appropriate workflow for processing a user prompt.\n"
    "Choose one of the following workflows: 'chat', 'write', or 'auto'.\n"
    "'chat' is for simply responding to the user, "
    "'write' writes the output to a given file and "
    "'auto' processes input files one by one.\n"
)

AUTO_ENGINEER_PROMPT_SYSTEM_MESSAGE = (
    "You are a prompt engineer, take the following prompt and rewrite it augmenting it in line with prompt engineering "
    "standards. Increase clarity, state facts simply, use step by step reasoning. "
    "If I include text/code as reference, please consider keeping it as is, provided it makes sense for the request as "
    "a whole. "
    "Returning *only* the new and improved version of my prompt, without answering it, as if I had written it myself."
)

QUESTION_PROMPT_SYSTEM_MESSAGE = (
    "Given the following user prompt what are your questions, be concise and targeted.\n"
    "Just ask the questions you would like to know before answering my prompt, do not actually answer my prompt."
)

# Context


def string_of_existing_topics_prompt(user_topics: List[str]):
    return "Existing Topics: " + ", ".join(user_topics)


def select_topic_prompt(term: dict[str, str]):
    specifics = term.get("specifics")
    return "Topic : " + term.get("term", "") + \
           (", Specifics: " + term.get("specifics")) if specifics else ""


SCHEMA_FOR_CONCEPT_TERMS = (
    "For the given prompt, return an array of concepts that would help answer this prompt. "
    "The 'term' field should be simple, e.g., the actual word of the concept. You can use "
    "the 'specifics' field if there is a particular aspect you would prefer to explore.\n"
    "Example: 'Tell me about the capital of France.' -> "
    "[{\"term\": \"France\", \"specifics\": \"capital\"}, {\"term\": \"Paris\"}]"
)


SELECT_TOPIC_SYSTEM_MESSAGE = "Given the list of topics I gave you, just return the most appropriate from the list"


# Non-User Prompts


SIMPLE_SUMMARY_PROMPT = "Very quickly summarise what you just wrote and where you wrote it."


def for_each_focus_on_prompt(initial_message: str, focus_on: str, iteration_id: int = None) -> str:
    if iteration_id:
        return f"{initial_message}\n\nSpecifically focus on {focus_on} for iteration #{iteration_id}."
    else:
        return f"{initial_message}\n\nSpecifically focus on {focus_on}."


def determine_pages_prompt(multi_file_processing_enabled: bool = False) -> str:
    if multi_file_processing_enabled:
        return (
            "Give just a filename (with extension) that should be worked on given the following prompt. "
            "No commentary. "
            "If appropriate, write multiple files, the ones at the top of the class hierarchy first/on the top."
        )

    return (
        "Give just a filename (with extension) that should be worked on given the following prompt.\n"
        "No commentary. Select only one singular file alone."
    )


EXTRACT_SEARCH_TERMS_PROMPT = (
    "Extract a key phrase from the following prompt to use for an internet search. "
    "Respond with the phrases separated by commas only, without additional text."
)


def categorisation_system_messages(
        user_categorisation_instructions: str
) -> List[str]:
    return [
        f"{user_categorisation_instructions} ",
        (
            "The existing categories are supplied, by suggesting a new more appropriate category, said category will "
            "be created in the system."
        ),
        (
            "Categorize the data with the most suitable single-word answer."
            "Write it as a singular XML start tag: <result=\"(your_selection)\">"
        )
    ]


DETERMINE_PAGES_SCHEMA = (
    "Write your data as a list ('[' then ']') of tags ('<' then '>'), "
    "where the tag name itself is the file_name (including extension), "
    "with a parameter 'purpose' representing why you want to create this file given the initial user "
    "message."
    "Purpose: a brief explanation of why the file is being referenced or created, "
    "clarifying its role in the overall process.\n"
    "Format:\n"
    "[<file_name.txt purpose='How this file is expected to satisfy the following request'>]"
    "Example:\n"
    "Message: 'Create a function to calculate pi using the Leibniz formula' and graph the results "
    "visually using pandas' ->\n"
    "[<pi.py purpose='Create a functional to calculate pi using the Leibniz formula'>,\n"
    "<graph.py purpose='graph the results of pi.py using pandas'>]"
)


def category_instructions_prompt(category_name: str) -> str:
    return (
        f"Generate a concise and relevant system message to be used for future prompts in this category: {category_name}"
    )


# Functionality


DEFAULT_USER_CATEGORISATION_INSTRUCTIONS = (
    "Given the following prompt-response pair, think through step by step and explain your reasoning."
)


def categorisation_inputs(user_prompt: str, llm_response: str = None, category_names: List[dict[str, str]] = []) -> List[str]:
    response_part = ""
    if llm_response:
        response_part = f"\n<response>{llm_response}</response>"

    if len(category_names) > 0:
        existing_categories = f"Existing categories: {', '.join(category_names)}"
    else:
        existing_categories = "No categories yet created"

    return [
        f"<input>{user_prompt}</input>" + response_part,
        existing_categories
    ]


CATEGORY_INSTRUCTIONS_SYSTEM_MESSAGE = (
    "You are an assistant that takes a given category and any additional context, to responds with a helpful, "
    "precisely designed LLM system message that would be useful for this category."
    "These system messages will be used when adding to this category, they should be specific and tailored for the "
    "most likely use of this category by the user."
    "Respond only with this system message"
)

SELECT_COLOUR_SYSTEM_MESSAGE = (
    "You are a color expert. "
    "Assign a HEX color code that best represents the given category name.\n"
    "Provide only the HEX code without any additional text."
)

SUMMARISE_WHILE_RETAINING_DETAIL_SYSTEM_MESSAGE = (
    "summarise the following information while retaining essential details."
)

"""
ToDo: Documents are themselves are a powerful way of instructing the AI to follow tasks,
 but for now we will avoid this until we can trigger it more deliberately
"""
SUMMARISER_SYSTEM_INSTRUCTIONS = """Take the file input and summarise it in a sentence or two."""

DEFAULT_BEST_OF_SYSTEM_MESSAGE = (
    "Pick and choose from your prior answers to create the best possible answer to the users initial user_message"
)

DETECT_RELEVANT_HISTORY_SYSTEM_MESSAGE = (
    "Review the messages I've entered and am about to enter, check them against the Prompt History, "
    "write a list of number ids for the prompts.\n"
    "Be very harsh only include a message from the history if it DIRECTLY relates to the user message. "
    "Otherwise include NOTHING.\n"
    "Just the list of numbers in square brackets, no commentary",
)

