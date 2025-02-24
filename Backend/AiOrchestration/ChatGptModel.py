from AiOrchestration.AiModel import AiModel


class ChatGptModel(AiModel):
    CHAT_GPT_4_OMNI_MINI = ("gpt-4o-mini", 0.00000015, 0.0000006)
    CHAT_GPT_O3_MINI = ("o3-mini", 0.00000055, 0.0000044)
    CHAT_GPT_O1_MINI = ("o1-mini", 0.00000055, 0.0000044)
    CHAT_GPT_4_OMNI = ("gpt-4o", 0.0000025, 0.00001)

    @property
    def value(self) -> str:
        """Return the underlying model identifier required by the API."""
        return self._model_str

    @classmethod
    def get_default(cls) -> 'ChatGptModel':
        return cls.CHAT_GPT_4_OMNI_MINI
