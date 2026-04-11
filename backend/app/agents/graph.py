from __future__ import annotations

from app.agents.analysis import AnalysisAgent
from app.agents.anomaly import AnomalyAgent
from app.agents.driver_analysis import DriverAnalysisAgent
from app.agents.explanation import ExplanationAgent
from app.agents.forecast import ForecastAgent
from app.agents.insight import InsightAgent
from app.agents.intent import IntentAgent
from app.agents.multi_step_executor import MultiStepExecutor
from app.agents.planner import PlannerAgent
from app.agents.recommendation_engine import RecommendationEngine
from app.agents.schema_selector import SchemaSelector
from app.agents.semantic import SemanticAgent
from app.agents.sql_generator import SQLAgent
from app.agents.sql_validator import SQLValidator
from app.agents.state import AgentState
from app.core.config import Settings, get_settings
from app.schemas.api import IntelligenceResponse
from app.services.production_guard import (
    ConfidenceScorer,
    DataContractValidator,
    RequestGuard,
    ResponseConsistencyGuard,
    fail_closed,
)
from app.services.query_executor import QueryExecutor
from app.services.response_builder import build_response


class FinancialIntelligenceGraph:
    """
    Multi-agent Decision Intelligence Orchestrator.

    Two execution paths:

    SIMPLE PATH (analytics / forecast / anomaly):
      Intent → Semantic → Schema → SQL → Validate → Execute
      → [Forecast | Anomaly | Analysis] → Insight → Explain → Response

    COMPLEX PATH (multi-part questions with root cause + recommendations):
      Intent → Planner → MultiStepExecutor
      → DriverAnalysis → RecommendationEngine → Insight → Explain → Response
    """

    def __init__(
        self,
        executor: QueryExecutor,
        settings: Settings | None = None,
        **kwargs,
    ) -> None:
        self.settings            = settings or get_settings()
        self.executor            = executor
        self.intent_agent        = IntentAgent()
        self.planner             = PlannerAgent()
        self.multi_executor      = MultiStepExecutor(executor)
        self.driver_agent        = DriverAnalysisAgent()
        self.rec_engine          = RecommendationEngine(self.settings)
        self.schema_selector     = SchemaSelector()
        self.semantic_agent      = SemanticAgent()
        self.sql_agent           = SQLAgent(self.settings)
        self.validator           = SQLValidator(self.settings)
        self.analysis_agent      = AnalysisAgent()
        self.forecast_agent      = ForecastAgent(self.settings)
        self.anomaly_agent       = AnomalyAgent(self.settings)
        self.explanation_agent   = ExplanationAgent()
        self.insight_agent       = InsightAgent()
        self.request_guard       = RequestGuard(self.settings)
        self.data_validator      = DataContractValidator(self.settings)
        self.confidence_scorer   = ConfidenceScorer(self.settings)
        self.response_guard      = ResponseConsistencyGuard()

    # ── Main entry point ──────────────────────────────────────────────────────
    def run_sync(self, state: AgentState, *, horizon_days: int | None = None) -> IntelligenceResponse:
        if horizon_days is not None:
            state["horizon_days"] = horizon_days

        # ── Step 1: Intent ────────────────────────────────────────────────────
        state = self.intent_agent.classify(state)
        entities = state.get("intent", {}).get("entities", {})
        if not state.get("horizon_days") and isinstance(entities, dict) and entities.get("horizon_days"):
            state["horizon_days"] = int(entities["horizon_days"])
        intent     = state["intent"]["intent"]
        confidence = float(state["intent"].get("confidence", 0.0))

        # Early exits — no DB needed
        if intent in ("unsafe", "clarification", "out_of_scope", "conversational"):
            if intent == "unsafe":
                state["status"] = "blocked"
                state["validation_error"] = state["intent"].get("ambiguity")
            elif intent == "out_of_scope":
                state["status"] = "out_of_scope"
            elif intent == "conversational":
                state["status"] = "conversational"
            else:
                state["status"] = "needs_clarification"
            state["confidence"] = confidence
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        # ── COMPLEX PATH ──────────────────────────────────────────────────────
        if intent == "complex":
            return self._run_complex(state, confidence)

        # ── SIMPLE PATH ───────────────────────────────────────────────────────
        return self._run_simple(state, intent, confidence)

    # ── Complex multi-step path ───────────────────────────────────────────────
    def _run_complex(self, state: AgentState, confidence: float) -> IntelligenceResponse:
        # Step 2: Semantic + schema before trusting the plan
        state = self.semantic_agent.map(state)
        state = self.schema_selector.select(state)
        if state.get("schema_error"):
            state = fail_closed(state, "blocked", state["schema_error"])
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        date_guard = self.request_guard.validate_date_range(state)
        if not date_guard.ok:
            state = fail_closed(state, "blocked", date_guard.reason or "Invalid date range.")
            state = self.explanation_agent.explain(state)
            return self._to_response(state)
        if not state["date_range"].is_explicit:
            state["status"] = "needs_clarification"
            state["intent"]["ambiguity"] = "Which period should I use for this multi-step analysis?"
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        if state.get("intent", {}).get("has_forecast") and not state.get("horizon_days"):
            state["status"] = "needs_clarification"
            state["intent"]["ambiguity"] = "How many future days should I forecast?"
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        # Step 3: Plan
        state = self.planner.plan(state)

        # Step 4: Execute all plan steps
        state = self.multi_executor.execute(state)
        if state.get("status") in ("blocked", "insufficient_data", "error"):
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        # Step 5: Driver analysis (comparison + vendor/category breakdown)
        state = self.driver_agent.analyze(state)

        # Step 6: Recommendations
        state = self.rec_engine.generate(state)

        # Step 7: Insight layer
        state = self.insight_agent.generate(state)

        # Step 8: Compose final answer
        state["confidence"] = confidence
        state["status"]     = "success"
        state = self.explanation_agent.explain(state)

        # Use forecast chart if available
        if state.get("forecast_chart") and not state.get("chart"):
            state["chart"] = state["forecast_chart"]

        # Use current period rows for supporting data
        step_results = state.get("step_results", {})
        state["rows"]    = step_results.get("current_cashflow_rows", [])
        state["columns"] = list(state["rows"][0].keys()) if state["rows"] else []

        return self._to_response(state)

    # ── Simple single-step path ───────────────────────────────────────────────
    def _run_simple(self, state: AgentState, intent: str, confidence: float) -> IntelligenceResponse:
        # Step 2: Semantic mapping + time resolution
        state = self.semantic_agent.map(state)

        # Step 3: Schema context
        state = self.schema_selector.select(state)
        if state.get("schema_error"):
            state = fail_closed(state, "blocked", state["schema_error"])
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        date_guard = self.request_guard.validate_date_range(state)
        if not date_guard.ok:
            state = fail_closed(state, "blocked", date_guard.reason or "Invalid date range.")
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        time_required_tables = {"bank_transactions", "expenses"}
        selected_tables = set(state.get("schema_context", {}))
        if intent in ("analytics", "anomaly") and selected_tables & time_required_tables and not state["date_range"].is_explicit:
            state["status"] = "needs_clarification"
            state["intent"]["ambiguity"] = "Which time period should I analyze?"
            state = self.explanation_agent.explain(state)
            return self._to_response(state)
        if intent == "forecast" and not state.get("horizon_days"):
            state["status"] = "needs_clarification"
            state["intent"]["ambiguity"] = "How many future days should I forecast?"
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        # Step 4: SQL generation
        state = self.sql_agent.generate(state)
        if state.get("validation_error") and not state.get("sql"):
            state = fail_closed(state, "blocked", state["validation_error"])
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        # Step 5: SQL validation
        validation = self.validator.validate(
            state["sql"],
            business_id=int(state["business_id"]),
            schema_context=state.get("schema_context"),
        )
        if not validation.ok:
            state["status"]          = "blocked"
            state["validation_error"] = validation.error
            state["confidence"]       = max(0.0, confidence - 0.5)
            state = self.explanation_agent.explain(state)
            return self._to_response(state)
        state["sql"] = validation.sql

        # Step 6: Execute SQL
        try:
            columns, rows, truncated = self.executor._fetch_sync(validation.sql, validated=True)
        except Exception as exc:
            state = fail_closed(state, "error", f"Database query failed: {exc}")
            state = self.explanation_agent.explain(state)
            return self._to_response(state)
        if truncated:
            state.setdefault("warnings", []).append(
                f"Results truncated to {self.settings.max_result_rows} rows."
            )
        state["columns"]   = columns
        state["rows"]      = rows
        state["truncated"] = truncated

        contract = self.data_validator.validate(intent, rows, columns, state)
        if not contract.ok:
            state = fail_closed(state, "insufficient_data", contract.reason or "Data contract validation failed.")
            state = self.explanation_agent.explain(state)
            return self._to_response(state)

        state["confidence"] = self.confidence_scorer.score(
            base=confidence,
            rows_count=len(rows),
            validation_ok=True,
            schema_tables=len(state.get("schema_context", {})),
            warnings=state.get("warnings", []),
        )

        # Step 7: Post-processing
        if intent == "forecast":
            state = self.forecast_agent.forecast(state)
            if state.get("status") == "insufficient_data":
                state = self.explanation_agent.explain(state)
                return self._to_response(state)
        elif intent == "anomaly":
            state = self.anomaly_agent.detect(state)
        else:
            state = self.analysis_agent.analyze(state)

        # Step 8: Insights
        state = self.insight_agent.generate(state)

        # Step 9: Explanation
        state = self.explanation_agent.explain(state)

        return self._to_response(state)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _compute_confidence(self, base: float, rows_count: int) -> float:
        return self.confidence_scorer.score(
            base=base,
            rows_count=rows_count,
            validation_ok=rows_count > 0,
            schema_tables=1,
            warnings=[],
        )

    async def run(self, state: AgentState, *, horizon_days: int | None = None) -> IntelligenceResponse:
        return self.run_sync(state, horizon_days=horizon_days)

    def _to_response(self, state: AgentState) -> IntelligenceResponse:
        consistency = self.response_guard.validate(state)
        if not consistency.ok:
            state = fail_closed(state, "blocked", consistency.reason or "Response consistency validation failed.")
            state = self.explanation_agent.explain(state)
        return build_response(
            status=state.get("status", "success"),
            answer=state.get("answer", ""),
            explanation=state.get("explanation", ""),
            sql=state.get("sql"),
            rows=state.get("rows", []),
            columns=state.get("columns", []),
            truncated=bool(state.get("truncated", False)),
            chart=state.get("chart"),
            confidence=float(state.get("confidence", 0.0)),
            intent=state.get("intent", {}).get("intent"),
            analysis_method=(
                state.get("analysis", {}).get("method")
                or state.get("forecast", {}).get("method")
                or ("multi_step" if state.get("step_results") else None)
            ),
            warnings=state.get("warnings", []),
            follow_up_questions=state.get("follow_up_questions", []),
            recommendations=state.get("recommendations"),
            driver_analysis=state.get("driver_analysis"),
            summary=state.get("summary"),
            root_cause=state.get("root_cause"),
        )
