from hireme_ai.core.config import Settings
from hireme_ai.providers.embeddings.base import EmbeddingProvider
from hireme_ai.providers.embeddings.gemini import GeminiEmbeddingProvider


def create_embeddings(settings: Settings) -> EmbeddingProvider:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for live embeddings")
    return GeminiEmbeddingProvider(
        settings.gemini_api_key, settings.embedding_model, settings.embedding_dim
    )
