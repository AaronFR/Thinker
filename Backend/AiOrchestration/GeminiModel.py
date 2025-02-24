from AiOrchestration.AiModel import AiModel


class GeminiModel(AiModel):
    """OpenAI API Models"""
    GEMINI_2_FLASH = ("gemini-2.0-flash", 0.0000001, 0.0000004)
    GEMINI_2_FLASH_LITE_PREVIEW = ("gemini-2.0-flash-lite-preview", 0.000000075, 0.0000003)

    @property
    def value(self) -> str:
        """Return the underlying model identifier required by the API."""
        return self._model_str

    @classmethod
    def get_default(cls) -> 'GeminiModel':
        return cls.GEMINI_2_FLASH
