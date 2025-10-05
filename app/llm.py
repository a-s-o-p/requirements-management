from __future__ import annotations

import json
import os
from typing import Any, Dict, List

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - dependency loading handled at runtime
    OpenAI = None  # type: ignore


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM client cannot be configured."""


class LLMClient:
    """Thin wrapper around the OpenAI chat completion client."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.default_temperature = temperature
        self._client: OpenAI | None = None

    def _ensure_client(self) -> OpenAI:
        if self._client is not None:
            return self._client
        if OpenAI is None:
            raise LLMConfigurationError(
                "openai package is not available. Install it or adjust dependencies."
            )
        if not self.api_key:
            raise LLMConfigurationError(
                "OpenAI API key is not configured. Set OPENAI_API_KEY or pass api_key explicitly."
            )
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def _chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float | None = None,
        response_format: Dict[str, Any] | None = None,
    ) -> str:
        client = self._ensure_client()
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        if response_format:
            params["response_format"] = response_format
        response = client.chat.completions.create(**params)
        choice = response.choices[0]
        content = choice.message.content or ""
        return content.strip()

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self._chat(messages, temperature=temperature)

    def structured_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        content = self._chat(
            messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise LLMConfigurationError(
                "LLM response was not valid JSON. Adjust prompts or model configuration."
            ) from exc
