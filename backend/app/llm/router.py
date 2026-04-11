from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import httpx

from app.core.config import Settings, get_settings


class ModelRole(StrEnum):
    INTENT = "intent"
    SEMANTIC = "semantic"
    SQL = "sql"
    SQL_VALIDATOR = "sql_validator"
    ANALYSIS = "analysis"
    EXPLANATION = "explanation"
    FORECAST = "forecast"
    ANOMALY = "anomaly"


MODEL_MAP: dict[ModelRole, str] = {
    ModelRole.INTENT: "openai/gpt-oss-20b",
    ModelRole.SEMANTIC: "meta-llama/llama-4-scout-17b-16e-instruct",
    ModelRole.SQL: "openai/gpt-oss-120b",
    ModelRole.SQL_VALIDATOR: "openai/gpt-oss-20b",
    ModelRole.ANALYSIS: "qwen/qwen3-32b",
    ModelRole.EXPLANATION: "llama-3.3-70b-versatile",
    ModelRole.FORECAST: "openai/gpt-oss-20b",
    ModelRole.ANOMALY: "qwen/qwen3-32b",
}


@dataclass(frozen=True)
class LLMResult:
    content: str
    model: str
    used_llm: bool


class LLMRouter:
    """OpenAI-compatible LLM router.

    The agents are deterministic without this client. When configured, each
    agent role gets a preferred model while downstream validators still enforce
    schema and read-only safety.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def complete(
        self,
        role: ModelRole,
        system: str,
        user: str,
        *,
        temperature: float = 0.0,
        response_format: dict[str, Any] | None = None,
    ) -> LLMResult:
        model = MODEL_MAP[role]
        if not self.settings.enable_llm or not self.settings.llm_base_url or not self.settings.llm_api_key:
            return LLMResult(content="", model=model, used_llm=False)

        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=self.settings.query_timeout_seconds) as client:
            response = await client.post(
                self.settings.llm_base_url.rstrip("/") + "/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.llm_api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return LLMResult(content=data["choices"][0]["message"]["content"], model=model, used_llm=True)


def parse_json_object(raw: str) -> dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
