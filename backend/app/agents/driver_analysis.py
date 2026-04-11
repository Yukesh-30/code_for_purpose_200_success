from __future__ import annotations

from typing import Any

from app.agents.state import AgentState


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / abs(previous) * 100, 1)


def _fmt(n: float) -> str:
    return f"₹{abs(n):,.0f}"


class DriverAnalysisAgent:
    """
    Compares current vs previous period and identifies top contributors
    to cashflow change (vendors + categories).
    """

    def analyze(self, state: AgentState) -> AgentState:
        results = state.get("step_results", {})

        current  = results.get("current_cashflow",  {})
        previous = results.get("previous_cashflow", {})

        # ── Period comparison ─────────────────────────────────────────────────
        curr_net = float(current.get("net",  0))
        prev_net = float(previous.get("net", 0))
        curr_in  = float(current.get("inflow",  0))
        prev_in  = float(previous.get("inflow",  0))
        curr_out = float(current.get("outflow", 0))
        prev_out = float(previous.get("outflow", 0))

        net_change    = curr_net - prev_net
        net_pct       = _pct_change(curr_net, prev_net)
        inflow_change = curr_in  - prev_in
        outflow_change= curr_out - prev_out

        direction = "declined" if net_change < 0 else "improved"

        # ── Vendor drivers ────────────────────────────────────────────────────
        vendor_rows = results.get("vendor_drivers", [])
        top_vendors = [
            {
                "vendor":      r.get("vendor", "Unknown"),
                "spend":       float(r.get("total_spend", 0)),
                "pct":         float(r.get("pct_of_total", 0)),
                "txn_count":   int(r.get("txn_count", 0)),
            }
            for r in vendor_rows[:5]
        ]

        # ── Category drivers ──────────────────────────────────────────────────
        cat_rows = results.get("category_drivers", [])
        top_categories = [
            {
                "category":  r.get("category", "Unknown"),
                "spent":     float(r.get("total_spent", 0)),
                "pct":       float(r.get("pct_of_spend", 0)),
                "txn_count": int(r.get("txn_count", 0)),
            }
            for r in cat_rows[:5]
        ]

        # ── Build driver analysis dict ────────────────────────────────────────
        driver_analysis = {
            "direction":       direction,
            "net_change":      round(net_change, 2),
            "net_pct_change":  net_pct,
            "inflow_change":   round(inflow_change, 2),
            "outflow_change":  round(outflow_change, 2),
            "current":         current,
            "previous":        previous,
            "top_vendors":     top_vendors,
            "top_categories":  top_categories,
        }

        state["driver_analysis"] = driver_analysis

        # ── Build human-readable summary ──────────────────────────────────────
        lines = []

        if previous:
            sign = "↓" if net_change < 0 else "↑"
            lines.append(
                f"Cashflow {direction} by {_fmt(net_change)} ({abs(net_pct):.1f}%) "
                f"compared to the previous period. "
                f"Current net: {_fmt(curr_net)}, Previous net: {_fmt(prev_net)}."
            )
            if inflow_change < 0:
                lines.append(f"Inflow dropped by {_fmt(inflow_change)} ({abs(_pct_change(curr_in, prev_in)):.1f}%).")
            if outflow_change > 0:
                lines.append(f"Outflow increased by {_fmt(outflow_change)} ({abs(_pct_change(curr_out, prev_out)):.1f}%).")

        if top_vendors:
            vendor_str = ", ".join(
                f"{v['vendor']} ({_fmt(v['spend'])}, {v['pct']:.1f}%)"
                for v in top_vendors[:3]
            )
            lines.append(f"Top vendors by spend: {vendor_str}.")

        if top_categories:
            cat_str = ", ".join(
                f"{c['category']} ({_fmt(c['spent'])}, {c['pct']:.1f}%)"
                for c in top_categories[:3]
            )
            lines.append(f"Top expense categories: {cat_str}.")

        state["driver_summary"] = " ".join(lines)
        return state
