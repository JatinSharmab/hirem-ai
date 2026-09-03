from google import genai
from google.genai import types

from hireme_ai.providers.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model_name: str, dimension: int = 768) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.dimension = dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        contents: list[types.ContentUnion] = [
            types.Content(parts=[types.Part(text=value)]) for value in texts
        ]
        response = await self.client.aio.models.embed_content(
            model=self.model_name,
            contents=contents,
            config={"output_dimensionality": self.dimension},
        )
        embeddings = response.embeddings or []
        if len(embeddings) != len(texts) or any(
            not item.values or len(item.values) != self.dimension for item in embeddings
        ):
            raise ValueError("Embedding response has missing or incompatible vectors")
        return [list(item.values or []) for item in embeddings]
