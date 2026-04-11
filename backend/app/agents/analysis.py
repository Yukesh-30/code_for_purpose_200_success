from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from app.agents.nlp_engine import analyse, ChartType
from app.agents.state import AgentState
from app.schemas.api import ChartData


def _smart_chart(rows: list[dict], nlp_chart: str, keys: set[str]) -> ChartData:
    """Pick the best chart type based on semantic result + data shape."""
    if not rows:
        return ChartData(type="none")

    # Pie requested and we have a groupable dimension
    if nlp_chart == "pie" and any(k in keys for k in (
        "category", "expense_category", "vendor", "merchant_name",
        "total_spent", "total_amount", "total_spend",
    )):
        dim = next((k for k in ("category", "expense_category", "merchant_name",
                                "vendor", "customer_name") if k in keys), None)
        val = next((k for k in ("total_spent", "total_amount", "total_spend",
                                "amount", "payment_amount", "invoice_amount") if k in keys), None)
        if dim and val:
            return ChartData(type="pie", x=dim, y=[val], series=rows[:20])

    # Time-series → line/area
    if any(k in keys for k in ("cashflow_date", "transaction_date", "forecast_date")):
        x_key = next(k for k in ("cashflow_date", "transaction_date", "forecast_date") if k in keys)
        y_keys = [k for k in ("inflow", "outflow", "net_cashflow",
                               "predicted_inflow", "predicted_outflow",
                               "predicted_closing_balance") if k in keys]
        if y_keys:
            chart_t = nlp_chart if nlp_chart in ("line", "area") else "line"
            return ChartData(type=chart_t, x=x_key, y=y_keys, series=rows)

    # Category/vendor aggregated → bar or pie
    if any(k in keys for k in ("total_spent", "total_amount", "total_spend")):
        dim = next((k for k in ("category", "expense_category", "merchant_name",
                                "vendor", "customer_name") if k in keys), None)
        val = next((k for k in ("total_spent", "total_amount", "total_spend",
                                "amount") if k in keys), None)
        if dim and val:
            chart_t = nlp_chart if nlp_chart in ("pie", "bar") else "bar"
            return ChartData(type=chart_t, x=dim, y=[val], series=rows[:15])

    # Invoice / vendor / loan → table
    if any(k in keys for k in ("invoice_number", "vendor_name", "loan_type",
                                "lender_name", "status", "due_date")):
        return ChartData(type="table", series=rows[:50])

    # Risk scores → bar
    if "liquidity_score" in keys:
        return ChartData(type="bar", x="forecast_date",
                         y=["liquidity_score", "default_risk_score",
                            "overdraft_risk_score", "working_capital_score"],
                         series=rows)

    return ChartData(type="table", series=rows[:50])


class AnalysisAgent:
    def analyze(self, state: AgentState) -> AgentState:
        rows     = state.get("rows", [])
        question = state.get("question", "").lower()
        parsed   = state.get("parsed_query")

        if not rows:
            state["status"]   = "insufficient_data"
            state["analysis"] = {"reason": "No rows returned for the requested business and period."}
            state["chart"]    = ChartData(type="none")
            return state

        # Resolve chart type from SemanticParser (preferred) or nlp_engine fallback
        # nlp_chart is always a plain string — no attribute access on undefined vars
        if parsed and parsed.chart_type:
            nlp_chart: str = parsed.chart_type
        else:
            nlp_chart = analyse(question).chart_type

        keys = set(rows[0].keys())

        # ── Cashflow time-series ──────────────────────────────────────────────
        if {"inflow", "outflow", "net_cashflow"}.issubset(keys):
            totals = {
                "inflow":       sum(float(r.get("inflow")       or 0) for r in rows),
                "outflow":      sum(float(r.get("outflow")      or 0) for r in rows),
                "net_cashflow": sum(float(r.get("net_cashflow") or 0) for r in rows),
            }
            state["analysis"] = {
                "totals":                     totals,
                "average_daily_net_cashflow": mean(float(r.get("net_cashflow") or 0) for r in rows),
                "drivers":                    self._top_drivers(rows),
                "method":                     "cashflow_aggregation",
            }
            state["chart"] = _smart_chart(rows, nlp_chart, keys)

        # ── Category / expense breakdown ──────────────────────────────────────
        elif "expense_category" in keys or ("category" in keys and "total_spent" not in keys):
            by_cat: dict[str, float] = defaultdict(float)
            for r in rows:
                cat = str(r.get("expense_category") or r.get("category") or "Other")
                by_cat[cat] += float(r.get("amount") or r.get("total_spent") or 0)
            agg_rows = [{"category": k, "total_amount": round(v, 2)}
                        for k, v in sorted(by_cat.items(), key=lambda x: -x[1])]
            state["analysis"] = {
                "by_category": dict(by_cat),
                "row_count":   len(rows),
                "method":      "category_aggregation",
            }
            chart_t = "pie" if nlp_chart == "pie" or any(
                w in question for w in ("across", "sector", "breakdown", "distribution", "proportion")
            ) else "bar"
            state["chart"] = ChartData(type=chart_t, x="category",
                                       y=["total_amount"], series=agg_rows[:15])

        # ── Pre-aggregated category data ──────────────────────────────────────
        elif "total_spent" in keys and "category" in keys:
            chart_t = "pie" if nlp_chart == "pie" or any(
                w in question for w in ("across", "sector", "breakdown", "distribution")
            ) else "bar"
            state["analysis"] = {"row_count": len(rows), "method": "category_breakdown"}
            state["chart"] = ChartData(type=chart_t, x="category",
                                       y=["total_spent"], series=rows[:15])

        # ── Vendor breakdown ──────────────────────────────────────────────────
        elif "vendor_name" in keys or "merchant_name" in keys:
            dim = "merchant_name" if "merchant_name" in keys else "vendor_name"
            val = next((k for k in ("total_spend", "payment_amount", "amount") if k in keys),
                       "payment_amount")
            state["analysis"] = {"row_count": len(rows), "method": "vendor_breakdown"}
            state["chart"] = ChartData(type="bar", x=dim, y=[val], series=rows[:10])

        # ── Transaction list ──────────────────────────────────────────────────
        elif "transaction_type" in keys and "amount" in keys:
            by_type: dict[str, float] = defaultdict(float)
            for r in rows:
                by_type[str(r.get("transaction_type"))] += float(r.get("amount") or 0)
            state["analysis"] = {
                "totals_by_type": dict(by_type),
                "row_count":      len(rows),
                "method":         "transaction_aggregation",
            }
            state["chart"] = _smart_chart(rows, nlp_chart, keys)

        # ── Everything else ───────────────────────────────────────────────────
        else:
            state["analysis"] = {"row_count": len(rows), "sample": rows[:5], "method": "generic"}
            state["chart"]    = _smart_chart(rows, nlp_chart, keys)

        state["status"] = "success"
        return state

    def _top_drivers(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(rows, key=lambda r: abs(float(r.get("net_cashflow") or 0)), reverse=True)[:5]
