from AiOrchestration.ChatGptModel import find_enum_value as find_chat_gpt_model, ChatGptModel
from AiOrchestration.ChatGptWrapper import ChatGptWrapper
from AiOrchestration.GeminiModel import find_enum_value as find_gemini_model, GeminiModel
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


def find_model_enum_value(model_string: str):
    if model_string in chat_gpt_models:
        return find_chat_gpt_model(model_string)
    elif model_string in gemini_models:
        return find_gemini_model(model_string)
    else:
        raise f"Invalid model! {model_string}"
