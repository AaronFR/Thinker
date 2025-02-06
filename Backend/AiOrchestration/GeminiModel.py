import enum


class GeminiModel(enum.Enum):
    """OpenAI API Models"""
    GEMINI_2_FLASH = "gemini-2.0-flash"
    GEMINI_2_FLASH_LITE_PREVIEW = "gemini-2.0-flash-lite-preview"


def find_enum_value(model_name: str = None):
    """
    Search for the corresponding enum value based on the model name provided.
    Otherwise, defaulting to the standard model.

    :param model_name: The model name to search for.
    :type model_name: str
    :return: Corresponding enum member if found; otherwise, None.
    :rtype: GeminiModel or Gemini 2.0 Flash by default
    """
    for model in GeminiModel:
        if model.value == model_name:
            return model
    return GeminiModel.GEMINI_2_FLASH
