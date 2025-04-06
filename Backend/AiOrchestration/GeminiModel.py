from AiOrchestration.AiModel import AiModel


class GeminiModel(AiModel):
    """OpenAI API Models"""
    GEMINI_2_FLASH = ("gemini-2.0-flash", 0.0000001, 0.0000004)
    GEMINI_2_FLASH_LITE = ("gemini-2.0-flash-lite", 0.000000075, 0.0000003)
    GEMINI_2_PRO_PREVIEW = ("gemini-2.5-pro-preview-03-25", 0.00000125, 0.00001)

    @property
    def value(self) -> str:
        """Return the underlying model identifier required by the API."""
        return self._model_str

    @classmethod
    def get_default(cls) -> 'GeminiModel':
        return cls.GEMINI_2_FLASH
