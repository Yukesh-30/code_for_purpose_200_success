from __future__ import annotations

from typing import Any, Literal, TypedDict

from app.schemas.api import ChartData, ChatMessage, SupportingData
from app.semantic.retriever import SemanticMapping
from app.services.time_context import DateRange


IntentName = Literal["analytics", "forecast", "anomaly", "clarification", "unsafe", "complex", "out_of_scope", "conversational"]


class IntentResult(TypedDict, total=False):
    intent: IntentName
    confidence: float
    ambiguity: str | None
    requires_sql: bool
    is_complex: bool
    has_forecast: bool
    has_anomaly: bool


class AgentState(TypedDict, total=False):
    # ── Input ─────────────────────────────────────────────────────────────────
    business_id: int
    user_id: int | None
    question: str
    history: list[ChatMessage]
    as_of_date: Any
    horizon_days: int

    # ── Intent + Plan ─────────────────────────────────────────────────────────
    intent: IntentResult
    plan: dict[str, Any]
    parsed_query: Any          # ParsedQuery from SemanticParser

    # ── Semantic + Schema ─────────────────────────────────────────────────────
    date_range: DateRange
    semantic_mapping: SemanticMapping
    schema_context: dict[str, list[str]]

    # ── Single-step pipeline ──────────────────────────────────────────────────
    sql: str
    validation_error: str | None
    rows: list[dict[str, Any]]
    columns: list[str]
    truncated: bool

    # ── Multi-step pipeline ───────────────────────────────────────────────────
    step_results: dict[str, Any]       # keyed by result_key from plan steps
    driver_analysis: dict[str, Any]    # comparison + top vendors/categories
    driver_summary: str                # human-readable driver narrative
    recommendations: list[dict]        # top 3 actions [{priority, action, reason, impact}]

    # ── Analysis & Inference ──────────────────────────────────────────────────
    analysis: dict[str, Any]
    forecast: dict[str, Any]
    anomalies: list[dict[str, Any]]
    forecast_chart: ChartData

    # ── Presentation ─────────────────────────────────────────────────────────
    confidence: float
    warnings: list[str]
    follow_up_questions: list[str]
    answer: str
    explanation: str
    summary: str           # one-line period summary
    root_cause: str        # root cause narrative
    status: str
    chart: ChartData
    supporting_data: SupportingData
