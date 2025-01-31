
def plan_file_creation(initial_message: str, file_name: str):
    statement = (
        f"<user_prompt>{initial_message}</user_prompt>: To start with narrow your focus on "
        f"{file_name} and think through how to change or write it to fulfill the user's prompt to the highest standard,"
        "step by step. "
        "Discuss what we know, identify specifically what the user wants accomplished, goals and "
        f"sub-goals, and any existing flaws or defects WITHOUT writing any text or code for {file_name}. \n"
        "You are just writing up a plan of action instructing the LLM to follow how to rewrite or write the file "
        "in line with this plan and specifying that this plan is to be replaced with the actual functioning "
        "file."
    )

    return statement


def write_file(file_name: str, purpose: str):
    statement = (
        f"Write/Rewrite {file_name} based on your previous plan of action for this particular file, "
        f"focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
        "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
        "Unless explicitly requested, the file's content must be preserved by default."
    )

    return statement


def plan_pages_to_write(page_count: int):
    return (
        "Provide a Markdown list of prompts to create a series of pages based on the following user message. "
        "Each prompt corresponds to one 'page'. Ensure that all prompts are clear, concise, and collectively "
        "provide valid and comprehensive instructions to fully satisfy the user's needs. If necessary, "
        "think through the problem outside of the list of prompts. "
        f"I expect {page_count} prompts. No more, no less."
    )


def write_code_file(file_name: str, purpose: str):
    statement = (
        f"Write/Rewrite {file_name} based on your previous plan of action and the actual contents of "
        f"this particular file, focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
        "Making sure that the file imports as necessary, referencing the appropriate classes. "
        "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
        "Unless explicitly requested, the file's content must be preserved by default."
        "Finally, understand what you did or did not do, if you can see a file in your history that was they way they"
        "WERE, its YOUR job to change the file in line with the users prompt, not act like you've written code you "
        "haven't."
    )

    return statement
