from typing import Any

from google import genai
from google.genai import types

from hireme_ai.providers.llm.base import LLMProvider, T


def generation_schema(value: Any) -> Any:
    """Use portable schema constraints for generation; validate all bounds locally."""
    unsupported = {"minLength", "maxLength", "minimum", "maximum", "minItems", "maxItems"}
    if isinstance(value, dict):
        return {
            key: generation_schema(item) for key, item in value.items() if key not in unsupported
        }
    if isinstance(value, list):
        return [generation_schema(item) for item in value]
    return value


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> str:
        client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=45000))
        async with client.aio as session:
            response = await session.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0, max_output_tokens=2048),
            )
        return response.text or ""

    async def generate_structured(self, prompt: str, schema: type[T]) -> T:
        client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=45000))
        async with client.aio as session:
            response = await session.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=generation_schema(schema.model_json_schema()),
                    temperature=0,
                    max_output_tokens=8192,
                ),
            )
        return schema.model_validate_json(response.text or "{}")
