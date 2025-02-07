from AiOrchestration.AiModel import AiModel


class ChatGptModel(AiModel):
    """OpenAI API Models"""
    CHAT_GPT_4_OMNI_MINI = "gpt-4o-mini"
    CHAT_GPT_4_OMNI = "gpt-4o"
    CHAT_GPT_O1_MINI = "o1-mini"
    CHAT_GPT_O1_PREVIEW = "o1-preview"

    @classmethod
    def get_default(cls) -> 'ChatGptModel':
        return cls.CHAT_GPT_4_OMNI_MINI
