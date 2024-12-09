import enum


class ChatGptModel(enum.Enum):
    """OpenAI API Models"""
    CHAT_GPT_4_OMNI_MINI = "gpt-4o-mini"
    CHAT_GPT_4_OMNI = "gpt-4o"
    CHAT_GPT_O1_MINI = "o1-mini"
    CHAT_GPT_O1_PREVIEW = "o1-preview"


def find_enum_value(model_name: str = None):
    """
    Search for the corresponding enum value based on the model name provided.
    Otherwise, defaulting to the standard model.

    :param model_name: The model name to search for.
    :type model_name: str
    :return: Corresponding enum member if found; otherwise, None.
    :rtype: ChatGptModel or 4o Mini by default
    """
    for model in ChatGptModel:
        if model.value == model_name:
            return model
    return ChatGptModel.CHAT_GPT_4_OMNI_MINI
