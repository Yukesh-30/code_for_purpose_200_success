from __future__ import annotations

import re
from datetime import date

from app.agents.state import AgentState
from app.services.time_context import TimeContextResolver, parse_period_months


class PlannerAgent:
    """
    Deterministic multi-step planner — no LLM required.
    Uses calendar-aware date arithmetic for all period calculations.
    """

    def plan(self, state: AgentState) -> AgentState:
        question    = state.get("question", "").lower()
        intent      = state.get("intent", {})
        today       = state.get("as_of_date") or TimeContextResolver().today()

        # ── Detect what the user wants ────────────────────────────────────────
        wants_comparison = any(w in question for w in (
            "compare", "compared", "versus", "vs", "decline", "drop",
            "fell", "decreased", "why", "reason", "cause", "increased",
        ))
        wants_vendors    = any(w in question for w in ("vendor", "vendors", "supplier", "merchant"))
        wants_categories = any(w in question for w in ("categor", "expense", "spending", "cost", "breakdown"))
        wants_forecast   = intent.get("has_forecast") or any(w in question for w in (
            "forecast", "predict", "30 days", "60 days", "run out", "will i",
        ))
        wants_recs       = any(w in question for w in (
            "action", "actions", "recommend", "what should", "how to", "suggest",
        ))

        # ── Calendar-aware period calculation ─────────────────────────────────
        curr_start, curr_end, prev_start, prev_end, n_months = parse_period_months(question, today)

        steps = []

        # Step 1: Current period cashflow
        steps.append({
            "id":          1,
            "action":      "cashflow_summary",
            "description": f"Cashflow {curr_start} → {curr_end} ({n_months} month{'s' if n_months>1 else ''})",
            "start":       curr_start.isoformat(),
            "end":         curr_end.isoformat(),
            "result_key":  "current_cashflow",
        })

        # Step 2: Previous period cashflow (comparison)
        if wants_comparison:
            steps.append({
                "id":          2,
                "action":      "cashflow_summary",
                "description": f"Cashflow {prev_start} → {prev_end} (prior {n_months} month{'s' if n_months>1 else ''})",
                "start":       prev_start.isoformat(),
                "end":         prev_end.isoformat(),
                "result_key":  "previous_cashflow",
            })

        # Step 3: Vendor breakdown
        if wants_vendors or wants_comparison:
            steps.append({
                "id":          3,
                "action":      "vendor_breakdown",
                "description": f"Top vendors by spend {curr_start} → {curr_end}",
                "start":       curr_start.isoformat(),
                "end":         curr_end.isoformat(),
                "result_key":  "vendor_drivers",
            })

        # Step 4: Category breakdown
        if wants_categories or wants_comparison:
            steps.append({
                "id":          4,
                "action":      "category_breakdown",
                "description": f"Top expense categories {curr_start} → {curr_end}",
                "start":       curr_start.isoformat(),
                "end":         curr_end.isoformat(),
                "result_key":  "category_drivers",
            })

        # Step 5: Forecast (uses all available validated history up to today)
        if wants_forecast:
            steps.append({
                "id":           5,
                "action":       "forecast",
                "description":  f"Cashflow forecast from available history through {today}",
                "start":        None,
                "end":          today.isoformat(),
                "result_key":   "forecast",
                "horizon_days": state.get("horizon_days"),
            })

        # Step 6: Recommendations
        if wants_recs or wants_comparison:
            steps.append({
                "id":           6,
                "action":       "recommendations",
                "description":  "Generate top 3 actionable recommendations",
                "result_key":   "recommendations",
                "dependencies": [s["id"] for s in steps],
            })

        state["plan"] = {
            "intent":     intent.get("intent", "complex"),
            "complexity": "multi_step" if len(steps) > 1 else "simple",
            "steps":      steps,
            "n_months":   n_months,
            "periods": {
                "current":  {"start": curr_start.isoformat(), "end": curr_end.isoformat()},
                "previous": {"start": prev_start.isoformat(), "end": prev_end.isoformat()},
            },
        }

        return state
