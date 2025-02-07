from AiOrchestration.AiModel import AiModel
from AiOrchestration.ChatGptModel import ChatGptModel
from AiOrchestration.ChatGptWrapper import ChatGptWrapper
from AiOrchestration.GeminiModel import GeminiModel
from AiOrchestration.GeminiWrapper import GeminiWrapper

chat_gpt_models = {model.value for model in ChatGptModel}
gemini_models = {model.value for model in GeminiModel}


def determine_prompter(model_string: str):
    if model_string in chat_gpt_models:
        return ChatGptWrapper()
    elif model_string in gemini_models:
        return GeminiWrapper()
    else:
        raise f"Invalid model! {model_string}"


def find_model_enum_value(model_string: str) -> AiModel:
    if model_string in chat_gpt_models:
        return ChatGptModel.find_enum_value(model_string)
    elif model_string in gemini_models:
        return GeminiModel.find_enum_value(model_string)
    else:
        raise f"Invalid model! {model_string}"
