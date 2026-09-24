from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock_provider import MockLLMProvider
from app.core.config import settings


def get_llm_provider() -> BaseLLMProvider:
    """Returns configured LLM provider according to environment settings."""
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "mock":
        return MockLLMProvider()

    # Ready for plug-in of OpenAI, Gemini, Claude, Groq
    # Fallback to mock if API key is mock or missing
    if settings.LLM_API_KEY.startswith("mock"):
        return MockLLMProvider()

    return MockLLMProvider()
