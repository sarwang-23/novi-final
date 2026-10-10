from abc import ABC, abstractmethod
from typing import Any


class LLMError(Exception):
    """Raised when the LLM provider fails to produce a usable result."""


class LLMProvider(ABC):
    """Contract for any LLM backend Novi talks through."""

    @abstractmethod
    async def complete(self, prompt: str, system: str | None = None) -> str:
        ...

    @abstractmethod
    async def complete_json(self, prompt: str, system: str | None = None) -> Any:
        ...

    async def complete_grounded(self, prompt: str, system: str | None = None) -> dict:
        """Web-search grounded completion. Providers without grounding support
        just return the plain completion (no sources)."""
        text = await self.complete(prompt, system=system)
        return {"text": text, "sources": []}