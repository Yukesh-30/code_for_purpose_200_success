from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime | None = None


class ChatRequest(BaseModel):
    business_id: int = Field(gt=0)
    user_id: int | None = Field(default=None, gt=0)
    session_id: str | None = None
    question: str = Field(min_length=2, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    as_of_date: date | None = None
    include_sql: bool = True


class ForecastRequest(BaseModel):
    business_id: int = Field(gt=0)
    user_id: int | None = Field(default=None, gt=0)
    horizon_days: int = Field(ge=1, le=180)
    as_of_date: date | None = None
    include_sql: bool = True


class AnomalyRequest(BaseModel):
    business_id: int = Field(gt=0)
    user_id: int | None = Field(default=None, gt=0)
    lookback_days: int = Field(ge=7, le=730)
    as_of_date: date | None = None
    include_sql: bool = True


class SupportingData(BaseModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    truncated: bool = False


class ChartData(BaseModel):
    type: Literal["line", "bar", "table", "none", "pie", "area"] = "none"
    x: str | None = None
    y: list[str] = Field(default_factory=list)
    series: list[dict[str, Any]] = Field(default_factory=list)


class Recommendation(BaseModel):
    priority: int = 1
    action: str
    reason: str
    impact: Literal["high", "medium", "low"] = "medium"


class IntelligenceResponse(BaseModel):
    status: Literal["success", "needs_clarification", "insufficient_data", "blocked", "error", "out_of_scope"]
    answer: str
    explanation: str
    sql: str | None = None
    supporting_data: SupportingData = Field(default_factory=SupportingData)
    chart: ChartData = Field(default_factory=ChartData)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    intent: str | None = None
    analysis_method: str | None = None
    warnings: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    # Structured decision intelligence fields
    summary: str | None = None
    root_cause: str | None = None
    recommendations: list[dict[str, Any]] | None = None
    driver_analysis: dict[str, Any] | None = None
