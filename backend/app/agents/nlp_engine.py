from __future__ import annotations

"""
NLP Engine — extracts structured intent from natural language questions.
Determines: required tables, chart type, aggregation, time range, entities.
No external NLP library required — uses weighted keyword matching + pattern rules.
"""

import re
from dataclasses import dataclass, field
from typing import Literal

ChartType = Literal["pie", "bar", "line", "area", "table", "none"]
AggType   = Literal["sum", "count", "avg", "trend", "compare", "distribution"]


@dataclass
class NLPResult:
    # What tables are needed
    tables:       list[str]
    # What kind of chart fits best
    chart_type:   ChartType
    # What aggregation to perform
    aggregation:  AggType
    # Key dimension to group by (e.g. "category", "vendor", "month")
    group_by:     str | None
    # Whether the user wants a forecast
    wants_forecast: bool
    # Whether the user wants a comparison
    wants_compare:  bool
    # Detected entities (amounts, names, etc.)
    entities:     dict[str, str] = field(default_factory=dict)
    # Confidence 0-1
    confidence:   float = 0.8


# ── Table routing rules ───────────────────────────────────────────────────────
TABLE_RULES: list[tuple[tuple[str, ...], str]] = [
    (("invoice", "invoices", "customer payment", "receivable", "overdue invoice"), "invoice_records"),
    (("vendor", "supplier", "payable", "vendor payment"),                          "vendor_payments"),
    (("loan", "emi", "lender", "repayment", "outstanding loan"),                   "loan_obligations"),
    (("salary", "payroll", "employee", "staff cost", "wages"),                     "salary_schedule"),
    (("risk", "liquidity score", "default risk", "overdraft risk"),                "risk_scores"),
    (("expense", "expenses", "spending", "cost", "overhead"),                      "expenses"),
    (("recommend", "product", "banking product", "financing option"),              "banking_product_recommendations"),
    (("alert", "notification", "warning"),                                         "alerts"),
    (("transaction", "cashflow", "cash flow", "inflow", "outflow", "revenue",
      "income", "balance", "credit", "debit", "payment", "sale"),                 "bank_transactions"),
]

# ── Chart selection rules ─────────────────────────────────────────────────────
# (keywords) → chart_type
CHART_RULES: list[tuple[tuple[str, ...], ChartType]] = [
    (("breakdown", "distribution", "sector", "categor", "proportion",
      "share", "split", "composition", "across", "by type", "by category",
      "pie", "donut", "percentage"),                                               "pie"),
    (("trend", "over time", "daily", "weekly", "monthly", "timeline",
      "history", "historical", "time series", "line"),                            "line"),
    (("compare", "comparison", "versus", "vs", "top", "ranking",
      "highest", "lowest", "most", "least", "bar"),                               "bar"),
    (("forecast", "predict", "future", "projection", "next"),                     "area"),
    (("list", "show", "all", "table", "detail", "record"),                        "table"),
]

# ── Aggregation rules ─────────────────────────────────────────────────────────
AGG_RULES: list[tuple[tuple[str, ...], AggType]] = [
    (("total", "sum", "how much", "amount", "spend", "spent"),                    "sum"),
    (("how many", "count", "number of", "quantity"),                              "count"),
    (("average", "avg", "mean", "typical"),                                       "avg"),
    (("trend", "over time", "daily", "weekly", "monthly", "timeline"),            "trend"),
    (("compare", "versus", "vs", "difference", "change"),                         "compare"),
    (("breakdown", "distribution", "split", "across", "by"),                      "distribution"),
]

# ── Group-by dimension rules ──────────────────────────────────────────────────
GROUPBY_RULES: list[tuple[tuple[str, ...], str]] = [
    (("category", "categor", "sector", "type", "kind"),                           "category"),
    (("vendor", "supplier", "merchant"),                                           "merchant_name"),
    (("customer", "client"),                                                       "customer_name"),
    (("month", "monthly"),                                                         "month"),
    (("week", "weekly"),                                                           "week"),
    (("day", "daily"),                                                             "day"),
    (("payment mode", "mode", "upi", "neft", "rtgs"),                             "payment_mode"),
    (("status",),                                                                  "status"),
]


def _match(normalized: str, keywords: tuple[str, ...]) -> bool:
    return any(kw in normalized for kw in keywords)


def analyse(question: str) -> NLPResult:
    """Extract structured intent from a natural language question."""
    q = question.lower().strip()

    # ── Tables ────────────────────────────────────────────────────────────────
    tables: list[str] = []
    for keywords, table in TABLE_RULES:
        if _match(q, keywords):
            if table not in tables:
                tables.append(table)
    if not tables:
        tables = ["bank_transactions"]  # default

    # ── Chart type ────────────────────────────────────────────────────────────
    chart_type: ChartType = "line"  # default
    for keywords, ct in CHART_RULES:
        if _match(q, keywords):
            chart_type = ct
            break

    # Override: if only one table and it's not time-series, prefer bar/pie
    if "bank_transactions" not in tables and chart_type == "line":
        chart_type = "table"

    # ── Aggregation ───────────────────────────────────────────────────────────
    aggregation: AggType = "sum"
    for keywords, agg in AGG_RULES:
        if _match(q, keywords):
            aggregation = agg
            break

    # ── Group-by dimension ────────────────────────────────────────────────────
    group_by: str | None = None
    for keywords, dim in GROUPBY_RULES:
        if _match(q, keywords):
            group_by = dim
            break

    # ── Forecast / compare flags ──────────────────────────────────────────────
    wants_forecast = _match(q, ("forecast", "predict", "future", "next month",
                                "next quarter", "will i", "run out", "projection"))
    wants_compare  = _match(q, ("compare", "versus", "vs", "previous", "last vs",
                                "change", "difference", "decline", "growth"))

    # ── Confidence ────────────────────────────────────────────────────────────
    # More specific matches → higher confidence
    confidence = min(0.95, 0.6 + 0.05 * (len(tables) + (1 if group_by else 0)
                                          + (1 if wants_forecast else 0)))

    return NLPResult(
        tables=tables,
        chart_type=chart_type,
        aggregation=aggregation,
        group_by=group_by,
        wants_forecast=wants_forecast,
        wants_compare=wants_compare,
        confidence=confidence,
    )
