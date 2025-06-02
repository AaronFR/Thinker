from Data.Configuration import Configuration


def load_configuration() -> str:
    """Loads code style configuration settings from the configuration module.

    :return: A formatted string containing the coding guidelines.
    """
    config = Configuration.load_config()

    return config.get("system_messages", {}).get(
        "coder_worker_message",
        (
            "You are a talented, professional Senior developer, focused on efficient, professional coding and solving "
            "giving tasks to the best of your ability.\nThink through step by step. Write your reasoning *first* "
            "then, finally, write you response to my prompt. "
            "Write code in fenced markdown code blocks e.g.\n"
            "```python\n"
            "// your code snippet here\n"
            "```\n"
            "Remember if you are being passed a file, you didn't write it, don't take credit for work you didn't do "
            "and don't rest on your (imaginary) laurels' when work is to be done"
        )
    )
