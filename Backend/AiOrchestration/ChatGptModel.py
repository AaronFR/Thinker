from AiOrchestration.AiModel import AiModel


class ChatGptModel(AiModel):
    CHAT_GPT_4_POINT_ONE_NANO = ("gpt-4.1-nano", 0.0000001, 0.0000004)
    CHAT_GPT_4_POINT_ONE_MINI = ("gpt-4.1-mini", 0.0000004, 0.0000016)
    CHAT_GPT_O4_MINI = ("o4-mini", 0.0000011, 0.0000044)

    @property
    def value(self) -> str:
        """Return the underlying model identifier required by the API."""
        return self._model_str

    @classmethod
    def get_default(cls) -> 'ChatGptModel':
        return cls.CHAT_GPT_4_POINT_ONE_NANO
