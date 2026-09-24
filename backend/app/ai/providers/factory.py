from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.gemini_provider import GeminiLLMProvider
from app.ai.providers.mock_provider import MockLLMProvider
from app.core.config import settings


def get_llm_provider() -> BaseLLMProvider:
    """Returns configured LLM provider according to environment settings."""
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "gemini":
        return GeminiLLMProvider()

    if provider_name == "mock":
        return MockLLMProvider()

    # Fallback to mock if API key is missing or mock
    if settings.LLM_API_KEY.startswith("mock"):
        return MockLLMProvider()

    return MockLLMProvider()
