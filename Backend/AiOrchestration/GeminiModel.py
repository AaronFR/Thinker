from AiOrchestration.AiModel import AiModel


class GeminiModel(AiModel):
    """OpenAI API Models"""
    GEMINI_2_FLASH = "gemini-2.0-flash"
    GEMINI_2_FLASH_LITE_PREVIEW = "gemini-2.0-flash-lite-preview"

    @classmethod
    def get_default(cls) -> 'GeminiModel':
        return cls.GEMINI_2_FLASH
