from __future__ import annotations

from app.agents.state import AgentState
from app.core.config import Settings, get_settings


def _fmt(n: float) -> str:
    return f"₹{abs(n):,.0f}"


class RecommendationEngine:
    """
    Generates top 3 actionable recommendations based on:
    - Driver analysis (cashflow decline, top vendors, categories)
    - Forecast (negative days, ending balance)
    - Invoice health
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate(self, state: AgentState) -> AgentState:
        driver   = state.get("driver_analysis", {})
        forecast = state.get("step_results", {}).get("forecast", {})
        results  = state.get("step_results", {})

        recs: list[dict] = []

        # ── Forecast-based recommendations ────────────────────────────────────
        neg_days    = forecast.get("negative_cashflow_days", 0)
        end_balance = forecast.get("projected_ending_balance", 0)

        horizon_days = int(state.get("horizon_days") or self.settings.reserve_days_target)
        if neg_days > max(1, horizon_days // 6):
            recs.append({
                "priority": 1,
                "action":   "Accelerate invoice collections",
                "reason":   f"{neg_days} days of negative cashflow projected. "
                            "Chase overdue invoices immediately to improve liquidity.",
                "impact":   "high",
            })

        if end_balance < self.settings.low_balance_threshold:
            recs.append({
                "priority": 1,
                "action":   "Activate overdraft or credit line",
                "reason":   f"Projected ending balance of {_fmt(end_balance)} is critically low. "
                            "Pre-approve an overdraft facility before the gap hits.",
                "impact":   "high",
            })

        # ── Vendor-based recommendations ──────────────────────────────────────
        top_vendors = driver.get("top_vendors", [])
        if top_vendors:
            top_v = top_vendors[0]
            if top_v["pct"] > self.settings.vendor_concentration_threshold:
                recs.append({
                    "priority": 2,
                    "action":   f"Negotiate payment terms with {top_v['vendor']}",
                    "reason":   f"{top_v['vendor']} accounts for {top_v['pct']:.1f}% of total spend "
                                f"({_fmt(top_v['spend'])}). Extending payment terms by 30 days "
                                "would significantly improve working capital.",
                    "impact":   "medium",
                })

        # ── Category-based recommendations ────────────────────────────────────
        top_cats = driver.get("top_categories", [])
        if top_cats:
            top_c = top_cats[0]
            if top_c["pct"] > self.settings.category_concentration_threshold:
                recs.append({
                    "priority": 2,
                    "action":   f"Review and reduce {top_c['category']} expenses",
                    "reason":   f"{top_c['category']} is your largest expense category at "
                                f"{top_c['pct']:.1f}% of total spend ({_fmt(top_c['spent'])}). "
                                "Identify recurring vs one-time costs and cut discretionary items.",
                    "impact":   "medium",
                })

        # ── Cashflow decline recommendations ──────────────────────────────────
        net_pct = driver.get("net_pct_change", 0)
        outflow_change = driver.get("outflow_change", 0)
        inflow_change  = driver.get("inflow_change", 0)

        if net_pct < -15:
            if outflow_change > abs(inflow_change):
                recs.append({
                    "priority": 2,
                    "action":   "Implement expense approval controls",
                    "reason":   f"Outflow increased by {_fmt(outflow_change)} while inflow "
                                f"{'dropped' if inflow_change < 0 else 'stayed flat'}. "
                                f"Add approval gates for non-essential purchases above {_fmt(self.settings.expense_approval_threshold)}.",
                    "impact":   "medium",
                })
            else:
                recs.append({
                    "priority": 2,
                    "action":   "Launch a revenue recovery campaign",
                    "reason":   f"Inflow declined by {_fmt(abs(inflow_change))} ({abs(_pct_change_safe(inflow_change, driver.get('current', {}).get('inflow', 1))):.1f}%). "
                                "Offer early payment discounts to customers or accelerate pending deals.",
                    "impact":   "medium",
                })

        # ── Generic fallback if no specific signals ───────────────────────────
        if not recs:
            recs = [
                {
                    "priority": 3,
                    "action":   "Review monthly expense budget",
                    "reason":   "Regular expense review helps identify cost-saving opportunities.",
                    "impact":   "low",
                },
                {
                    "priority": 3,
                    "action":   "Set up automated invoice reminders",
                    "reason":   "Automated reminders reduce average collection time by 30-40%.",
                    "impact":   "low",
                },
                {
                    "priority": 3,
                    "action":   f"Maintain a {self.settings.reserve_days_target}-day cash reserve",
                    "reason":   "A configured operating cash buffer protects against seasonal dips.",
                    "impact":   "low",
                },
            ]

        # Sort by priority, keep top 3
        recs.sort(key=lambda r: r["priority"])
        state["recommendations"] = recs[:3]
        return state


def _pct_change_safe(change: float, base: float) -> float:
    if base == 0:
        return 0.0
    return change / abs(base) * 100
