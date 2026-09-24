from typing import Any

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMRequest, LLMResponse
from app.core.config import settings
from app.core.exceptions import LLMProviderError
from app.core.logging import logger


class GeminiLLMProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider calling the Gemini REST API via httpx.
    Supports gemini-1.5-flash, gemini-1.5-pro, and gemini-2.0-flash.
    """
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.LLM_API_KEY
        raw_model = (model or settings.LLM_MODEL or "gemini-1.5-flash").strip()
        # Map non-existent or experimental names like gemini-3.8-flash to valid Google AI Studio model
        if "3.8" in raw_model or "gemini-3" in raw_model:
            self.model = "gemini-1.5-flash"
        else:
            self.model = raw_model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key or self.api_key.startswith("mock"):
            raise LLMProviderError("Gemini API key is required when LLM_PROVIDER=gemini.")

        # Convert standardized messages into Gemini contents format
        contents = []
        system_instruction = None

        for msg in request.messages:
            if msg.role == "system":
                system_instruction = {
                    "parts": [{"text": msg.content}]
                }
            else:
                role = "model" if msg.role == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })

        gen_config: dict[str, Any] = {
            "temperature": request.temperature,
            "maxOutputTokens": request.max_tokens,
        }
        if request.json_mode:
            gen_config["responseMimeType"] = "application/json"

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": gen_config,
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        headers = {
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}?key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code != 200:
                    logger.error(f"Gemini API returned status {res.status_code}: {res.text}")
                    raise LLMProviderError(f"Gemini API error ({res.status_code}): {res.text}")

                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise LLMProviderError("No response candidates returned by Gemini.")

                parts = candidates[0].get("content", {}).get("parts", [])
                text_output = parts[0].get("text", "") if parts else ""

                # Strip markdown code blocks if returned by Gemini (e.g. ```json ... ```)
                cleaned_text = text_output.strip()
                if cleaned_text.startswith("```"):
                    lines = cleaned_text.splitlines()
                    if lines and lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    cleaned_text = "\n".join(lines).strip()

                return LLMResponse(
                    content=cleaned_text,
                    prompt_tokens=data.get("usageMetadata", {}).get("promptTokenCount", 0),
                    completion_tokens=data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    model=self.model,
                )
        except httpx.RequestError as exc:
            logger.error(f"Network error calling Gemini: {str(exc)}")
            raise LLMProviderError(f"Failed to reach Gemini API: {str(exc)}") from exc
