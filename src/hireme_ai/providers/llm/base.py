from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str: ...

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: type[T]) -> T: ...
