from hireme_ai.core.config import Settings
from hireme_ai.providers.llm.base import LLMProvider
from hireme_ai.providers.llm.gemini import GeminiProvider


def create_llm(settings: Settings) -> LLMProvider:
    if settings.llm_provider != "gemini":
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for live LLM mode")
    return GeminiProvider(settings.gemini_api_key, settings.llm_model)
