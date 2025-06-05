from Data.Configuration import Configuration


def load_configuration() -> str:
    """Loads code style configuration settings from the configuration module.

    :return: A formatted string containing the coding guidelines.
    """
    config = Configuration.load_config()

    return config.get("system_messages", {}).get(
        "default_worker_message",
        (
            "Be to the point"
        )
    )


DEFAULT_INSTRUCTIONS = "Analyze the user prompt in sequential order, giving priority to the most recent instructions " \
                       "provided by the user, to ensure accuracy in processing their requirements."
