from __future__ import annotations

from typing import Any

from app.schemas.api import ChartData, IntelligenceResponse, SupportingData


def build_response(
    *,
    status: str,
    answer: str,
    explanation: str,
    sql: str | None,
    rows: list[dict],
    columns: list[str],
    truncated: bool,
    chart: ChartData | None = None,
    confidence: float = 0.0,
    warnings: list[str] | None = None,
    follow_up_questions: list[str] | None = None,
    intent: str | None = None,
    analysis_method: str | None = None,
    recommendations: list[dict] | None = None,
    driver_analysis: dict[str, Any] | None = None,
    summary: str | None = None,
    root_cause: str | None = None,
) -> IntelligenceResponse:
    return IntelligenceResponse(
        status=status,
        answer=answer,
        explanation=explanation,
        sql=sql,
        supporting_data=SupportingData(
            columns=columns or [],
            rows=rows or [],
            row_count=len(rows or []),
            truncated=truncated,
        ),
        chart=chart or ChartData(),
        confidence=confidence,
        intent=intent,
        analysis_method=analysis_method,
        warnings=warnings or [],
        follow_up_questions=follow_up_questions or [],
        recommendations=recommendations,
        driver_analysis=driver_analysis,
        summary=summary,
        root_cause=root_cause,
    )
