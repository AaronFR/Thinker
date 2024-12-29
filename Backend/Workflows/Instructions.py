
def plan_file_creation(initial_message: str, file_name: str):
    statement = (
        f"<user_prompt>{initial_message}</user_prompt>: to start with we will narrow our focus on {file_name} "
        "and think through how to change it/write it so as to fulfill the user prompt, step by step, discussing "
        "what we know, identify specifically what they want accomplished, goals and sub-goals, "
        "and any existing flaws or defects WITHOUT writing any text or code for {file_name}. "
        "Just writing up a plan of action telling the LLM to follow how to rewrite/write the file in line with "
        "this plan and stating specifically that this plan is to be replaced with actual functioning file."
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


def write_code_file(file_name: str, purpose: str):
    statement = (
        f"Write/Rewrite {file_name} based on your previous plan of action and the actual contents of "
        f"this particular file, focusing on fulfilling the <purpose>{purpose}</purpose> for this file. "
        "Making sure that the file imports as necessary, referencing the appropriate classes. "
        "DO NOT OVERWRITE THIS FILE WITH A SUMMARY, do not include the contents of another file. "
        "Unless explicitly requested, the file's content must be preserved by default."
    )

    return statement



