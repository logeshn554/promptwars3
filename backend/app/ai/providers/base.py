from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class LLMRequest(BaseModel):
    messages: list[LLMMessage]
    temperature: float = 0.0
    max_tokens: int = 2000
    json_mode: bool = False

class LLMResponse(BaseModel):
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = "mock-model"

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Asynchronously call the LLM provider and return standardized response."""
        pass
