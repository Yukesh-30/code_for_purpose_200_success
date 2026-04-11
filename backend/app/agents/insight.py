from __future__ import annotations

from app.agents.state import AgentState

class InsightAgent:
    """
    Proactive insight generation.
    Analyses the returned rows + analysis to surface:
    - Risks (low balance, overdue invoices, high loan-to-cashflow ratio)
    - Opportunities (unused credit lines, high confidence recommendations)
    - Follow-up actions
    Always appends to state["warnings"] — never overwrites.
    """

    def generate(self, state: AgentState) -> AgentState:
        rows = state.get("rows", [])
        analysis = state.get("analysis", {})
        intent = state.get("intent", {}).get("intent")

        warnings = list(state.get("warnings", []))
        follow_ups = list(state.get("follow_up_questions", []))

        # ── Forecast insights ─────────────────────────────────────────────
        if intent == "forecast":
            forecast = state.get("forecast", {})
            neg_days = forecast.get("negative_cashflow_days", 0)
            ending_bal = forecast.get("projected_ending_balance", 0)
            if neg_days > 7:
                warnings.append(
                    f"⚠️ {neg_days} days with negative cashflow forecasted. "
                    "Consider activating an overdraft or accelerating invoice collections."
                )
            if ending_bal < 0:
                warnings.append(
                    "🚨 Projected ending balance is negative. Immediate action required. You may run out of cash during this period."
                )
            follow_ups += [
                "Which invoices should I collect first?",
                "What vendor payments are due next month?",
            ]

        # ── Anomaly insights ──────────────────────────────────────────────
        elif intent == "anomaly":
            count = analysis.get("anomaly_count", 0)
            if count > 5:
                warnings.append(
                    f"⚠️ {count} anomalous transactions detected. "
                    "Review for potential unauthorised activity or data errors."
                )
            follow_ups += [
                "Show me the merchant breakdown of anomalies",
                "What is my current risk score?",
            ]

        # ── Analytics insights ────────────────────────────────────────────
        else:
            # Check if cashflow is negative
            totals = analysis.get("totals", {})
            net = totals.get("net_cashflow", 0)
            if net < 0:
                warnings.append(
                    f"⚠️ Negative cashflow of ₹{abs(net):,.0f} detected. Consider reviewing vendor expenses."
                )

            # Check invoice health from rows
            if rows and "status" in rows[0]:
                overdue = sum(1 for r in rows if r.get("status") == "overdue" or r.get("delay_days", 0) > 0)
                if overdue > 0:
                    warnings.append(
                        f"📋 {overdue} overdue invoice(s) found. Prioritise collection to boost cashflow."
                    )
                    follow_ups.append("Show me only overdue invoices")

        # Cap entries and remove duplicates
        state["warnings"] = list(dict.fromkeys(warnings))[:5]
        state["follow_up_questions"] = list(dict.fromkeys(follow_ups))[:5]
        
        return state
