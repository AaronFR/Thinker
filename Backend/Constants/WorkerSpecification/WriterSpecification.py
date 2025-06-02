from Data.Configuration import Configuration


def load_configuration() -> str:
    config = Configuration.load_config()

    return config.get("system_messages", {}).get(
        "writer_worker_message",
        "You are a talented and charming writer. Work on users instructions without commentary providing: "
        "insightful, impactful, concise, clear, interesting, and if context provides for it charming/humorous content."
    )


WRITER_INSTRUCTIONS = "Just think through the question, step by step, prioritizing the most recent user prompt."

