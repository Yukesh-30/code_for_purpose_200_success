from __future__ import annotations

import json
import os
from typing import Any

import httpx

from app.core.config import get_settings


class LLMClient:
    """Thin wrapper around the Groq API (OpenAI-compatible)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.llm_api_key
        self.base_url = self.settings.llm_base_url.rstrip("/")
        self.model = "llama-3.3-70b-versatile"
        self.enabled = bool(self.settings.enable_llm and self.api_key)

    def chat(self, system: str, user: str, *, max_tokens: int = 512, temperature: float = 0.2) -> str | None:
        """
        Call the LLM. Returns the assistant text or None if LLM is disabled/fails.
        Always safe to call — falls back to None on any error.
        """
        if not self.enabled:
            return None
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    def json_chat(self, system: str, user: str, *, max_tokens: int = 512) -> dict[str, Any] | None:
        """Call LLM and parse JSON response. Returns None on failure."""
        raw = self.chat(system, user, max_tokens=max_tokens, temperature=0.1)
        if not raw:
            return None
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None


# Singleton
_client: LLMClient | None = None


def get_llm() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
