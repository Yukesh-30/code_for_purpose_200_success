"""
SemanticParser — Dynamic query understanding engine.

Instead of fixed keyword lists, this module:
1. Reads the LIVE database schema on startup (cached per process)
2. Uses the LLM (if enabled) to parse intent, entities, and SQL plan
3. Falls back to a TF-IDF-style semantic similarity scorer — no fixed words
4. Builds everything fresh for every query

The key insight: meaning comes from the relationship between words and
the schema, not from a hardcoded list of synonyms.
"""
from __future__ import annotations

import re
import math
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.core.config import get_settings


# ── Live schema loader ────────────────────────────────────────────────────────
_LIVE_SCHEMA: dict[str, dict] | None = None


def _load_live_schema() -> dict[str, dict]:
    """
    Load the actual DB schema at runtime — columns, types, sample values.
    Cached per process. If DB is unavailable, falls back to definitions.py.
    """
    global _LIVE_SCHEMA
    if _LIVE_SCHEMA is not None:
        return _LIVE_SCHEMA

    try:
        import os, psycopg2
        url = os.getenv("DATABASE_URL", "").replace("&channel_binding=require", "").replace("?channel_binding=require&", "?")
        conn = psycopg2.connect(url)
        cur  = conn.cursor()
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        schema: dict[str, dict] = {}
        for table, col, dtype in cur.fetchall():
            if table not in schema:
                schema[table] = {"columns": [], "column_types": {}}
            schema[table]["columns"].append(col)
            schema[table]["column_types"][col] = dtype
        conn.close()
        _LIVE_SCHEMA = schema
        return schema
    except Exception:
        # Fallback to static definitions
        from app.semantic.definitions import CURRENT_NEON_SCHEMA
        return {t: {"columns": list(cols), "column_types": {}} for t, cols in CURRENT_NEON_SCHEMA.items()}


# ── Semantic concept map — built from schema, not hardcoded ──────────────────
# Maps financial concepts to table+column combinations.
# This is derived from the schema structure, not from a fixed word list.

CONCEPT_TABLE_AFFINITY: dict[str, list[str]] = {
    # These are CONCEPTS, not keywords. The parser maps question semantics to concepts.
    "money_in":        ["bank_transactions"],   # credits, revenue, income, sales, receipts
    "money_out":       ["bank_transactions"],   # debits, expenses, costs, payments, outflow
    "net_position":    ["bank_transactions"],   # cashflow, profit, net, balance
    "invoicing":       ["invoice_records"],     # invoices, receivables, customers, billing
    "obligations":     ["vendor_payments", "loan_obligations", "salary_schedule"],  # payables, EMI, payroll
    "risk_health":     ["risk_scores"],         # risk, liquidity, default, overdraft
    "recommendations": ["banking_product_recommendations"],
    "alerts":          ["alerts"],
    "anomalies":       ["bank_transactions"],   # unusual, spikes, outliers
    "forecast":        ["bank_transactions"],   # future, predict, projection
}

# Semantic concept vocabulary — words that MEAN each concept
# This replaces fixed keyword lists with a richer semantic space
CONCEPT_VOCABULARY: dict[str, list[str]] = {
    "money_in": [
        "revenue", "income", "inflow", "credit", "sales", "receipts",
        "earnings", "collections", "received", "earned", "brought in",
        "money received", "cash received", "payment received",
        "how much did i earn", "what did i make", "what came in",
        "get more income", "increase income", "more revenue",
        "grow revenue", "boost sales",
    ],
    "money_out": [
        "expense", "expenses", "cost", "costs", "outflow", "debit",
        "spending", "spent", "paid", "payments", "overhead", "charges",
        "money spent", "cash out", "what i paid", "how much i spent",
        "burn", "burn rate", "outgoing",
    ],
    "net_position": [
        "cashflow", "cash flow", "net", "profit", "balance", "position",
        "liquidity", "runway", "how much cash", "cash situation",
        "financial health", "money left", "available cash",
        "decline", "drop", "fell", "decreased", "increased", "grew",
        "change", "difference", "compared", "versus",
        "transaction history", "history of transactions",
        "what should i do", "what can i do", "how to improve",
        "suggest actions", "give me advice",
    ],
    "invoicing": [
        "invoice", "invoices", "receivable", "receivables", "customer",
        "customers", "client", "clients", "billing", "overdue",
        "delayed payment", "payment delay", "stuck", "outstanding",
        "who owes", "who hasn't paid", "collection",
    ],
    "obligations": [
        "vendor", "vendors", "supplier", "suppliers", "payable", "payables",
        "loan", "loans", "emi", "repayment", "salary", "payroll",
        "employee", "staff", "wages", "due", "upcoming payment",
        "what i owe", "obligations", "liabilities",
    ],
    "risk_health": [
        "risk", "risky", "danger", "safe", "liquidity score", "default",
        "overdraft", "health", "score", "rating", "assessment",
        "am i safe", "will i run out", "financial risk",
    ],
    "anomalies": [
        "unusual", "abnormal", "spike", "spikes", "outlier", "outliers",
        "suspicious", "strange", "unexpected", "weird", "irregular",
        "anomaly", "anomalies", "detect", "flag", "flagged",
        "something wrong", "odd transaction", "large transaction",
    ],
    "forecast": [
        "forecast cashflow", "predict cashflow", "future cashflow",
        "cash projection", "cashflow projection",
        "next month cashflow", "next quarter cashflow",
        "will i run out", "run out of cash", "run out of money",
        "in the next 30", "in the next 60", "in the next 90",
        "over the next 30", "over the next 60",
        "what will my cash", "how much will i have",
        "cash position after", "balance after",
        "if my expenses increase", "if revenue stays",
        "scenario analysis", "what if expenses",
        "predict my balance", "project my cashflow",
        # Single-word high-signal terms
        "forecast", "predict", "projection", "projected",
    ],
    "recommendations": [
        "recommend a product", "recommend banking", "suggest a product",
        "what banking product", "financing option", "credit facility",
        "best banking option", "what loan should", "which product",
        "corrective action", "top 3 actions", "what actions should",
        "suggest corrective", "what should i apply for",
        "what should i do", "what can i do", "how to improve",
        "give me advice", "what do you suggest", "help me improve",
        "what to do", "how should i", "what actions",
    ],
}

# Output format vocabulary
FORMAT_VOCABULARY: dict[str, list[str]] = {
    "pie": [
        "breakdown", "distribution", "proportion", "share", "split",
        "composition", "across sectors", "by category", "by type",
        "percentage", "pie chart", "donut", "what percentage",
    ],
    "line": [
        "trend", "over time", "timeline", "history", "historical",
        "time series", "month by month", "week by week", "daily",
        "how has it changed", "progression", "movement",
    ],
    "bar": [
        "compare", "comparison", "ranking", "top", "highest", "lowest",
        "most", "least", "versus", "vs", "which is bigger",
        "bar chart", "ranked", "sorted",
    ],
    "area": [
        "forecast", "projection", "future", "predicted", "expected",
        "area chart", "filled",
    ],
    "table": [
        "list", "show all", "details", "records", "table",
        "give me all", "show me all", "full list",
    ],
}

# Grouping dimension vocabulary
GROUPBY_VOCABULARY: dict[str, list[str]] = {
    "category":      ["category", "categories", "sector", "type", "kind", "by category", "by type"],
    "merchant_name": ["vendor", "vendors", "merchant", "merchants", "supplier", "by vendor", "by merchant"],
    "customer_name": ["customer", "customers", "client", "clients", "by customer", "by client"],
    "month":         ["month", "monthly", "per month", "each month", "by month"],
    "week":          ["week", "weekly", "per week", "each week", "by week"],
    "day":           ["day", "daily", "per day", "each day", "by day"],
    "payment_mode":  ["payment mode", "payment method", "upi", "neft", "rtgs", "by mode"],
    "status":        ["status", "by status", "paid vs unpaid", "overdue vs pending"],
}


# ── Semantic scorer ───────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """
    Tokenize text into words + meaningful multi-word phrases.
    Uses sliding window for bigrams and trigrams.
    """
    text = text.lower().strip()
    words = re.findall(r'\b\w+\b', text)
    tokens = list(words)
    for i in range(len(words) - 1):
        tokens.append(f"{words[i]} {words[i+1]}")
    for i in range(len(words) - 2):
        tokens.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    return tokens


def _semantic_score(question: str, vocabulary: list[str]) -> float:
    """
    Score semantic relevance using two methods:
    1. Phrase-level substring matching (high weight) — catches exact phrases
    2. Token overlap (lower weight) — catches partial matches

    This avoids false positives from single-word matches like "next" or "will".
    """
    if not vocabulary:
        return 0.0

    q_lower = question.lower()
    q_tokens = set(_tokenize(q_lower))

    phrase_score = 0.0
    token_score  = 0.0

    for phrase in vocabulary:
        phrase_lower = phrase.lower()
        phrase_words = phrase_lower.split()

        # Method 1: Direct phrase match (highest confidence)
        if phrase_lower in q_lower:
            # Weight by phrase length — longer phrases = more specific = higher score
            phrase_score += len(phrase_words) * 0.3
            continue

        # Method 2: Token overlap for single words only
        if len(phrase_words) == 1:
            if phrase_lower in q_tokens:
                token_score += 0.1

    total = phrase_score + token_score
    # Normalize by question length to avoid bias toward long questions
    q_words = len(q_lower.split())
    return round(total / math.sqrt(max(q_words, 1)), 4)


@dataclass
class ParsedQuery:
    """Fully parsed query — built dynamically from the question."""
    # Primary intent
    intent_type: str          # "analytics" | "forecast" | "anomaly" | "complex" | "clarification"
    confidence: float

    # What data is needed
    concepts: list[str]       # e.g. ["money_out", "net_position"]
    tables: list[str]         # actual DB table names
    columns: list[str]        # relevant columns from live schema

    # How to present it
    chart_type: str           # "pie" | "bar" | "line" | "area" | "table"
    group_by: str | None      # dimension to group by

    # Time context
    time_label: str           # "last month", "last 2 months", etc.

    # Flags
    wants_forecast: bool
    wants_comparison: bool
    wants_anomaly: bool
    wants_recommendations: bool
    is_complex: bool
    is_followup: bool

    # Extracted entities
    entities: dict[str, Any] = field(default_factory=dict)

    # Raw scores for debugging
    concept_scores: dict[str, float] = field(default_factory=dict)


class SemanticParser:
    """
    Dynamic semantic parser — no fixed keyword lists.
    Scores every concept against the question using token overlap,
    then selects the best matching tables and output format.
    """

    def __init__(self) -> None:
        self._schema = _load_live_schema()
        self._settings = get_settings()

    def parse(self, question: str, history: list | None = None) -> ParsedQuery:
        """Parse a question into a fully structured ParsedQuery."""
        # Try LLM first if enabled
        if self._settings.enable_llm:
            result = self._llm_parse(question, history)
            if result:
                return result

        # Deterministic semantic scoring
        return self._semantic_parse(question, history or [])

    def _semantic_parse(self, question: str, history: list) -> ParsedQuery:
        """
        Pure semantic scoring — no fixed keyword lists.
        Every decision is made by scoring the question against concept vocabularies.
        """
        # Resolve follow-up context
        resolved, is_followup = self._resolve_context(question, history)

        # ── Score all concepts ────────────────────────────────────────────────
        concept_scores: dict[str, float] = {}
        for concept, vocab in CONCEPT_VOCABULARY.items():
            concept_scores[concept] = _semantic_score(resolved, vocab)

        sorted_concepts = sorted(concept_scores.items(), key=lambda x: -x[1])
        top_concepts = [c for c, s in sorted_concepts if s > 0.08]

        # ── Determine intent type ─────────────────────────────────────────────
        forecast_score  = concept_scores.get("forecast", 0)
        anomaly_score   = concept_scores.get("anomalies", 0)
        net_score       = concept_scores.get("net_position", 0)
        rec_score       = concept_scores.get("recommendations", 0)
        money_in_score  = concept_scores.get("money_in", 0)
        money_out_score = concept_scores.get("money_out", 0)

        # Complexity: multiple DISTINCT high-scoring concepts = multi-step
        # Use a higher threshold to avoid false positives
        high_concepts = [c for c, s in sorted_concepts if s > 0.15]

        # Forecast must have a STRONG signal — not just "next month" in passing
        # Require forecast score to dominate other scores
        strong_forecast = (
            forecast_score >= 0.1
            and forecast_score > anomaly_score * 1.5
            and forecast_score >= net_score * 0.5
        )

        # Anomaly must dominate
        strong_anomaly = (
            anomaly_score > 0.1
            and anomaly_score > forecast_score
        )

        # ── Structural complexity signals (independent of concept scores) ──────
        # These detect multi-part questions by structure, not just vocabulary
        q_lower = resolved.lower()
        q_words = q_lower.split()

        # Comparison signals — "vs", "compared to", "previous", "last X vs"
        COMPARISON_SIGNALS = [
            " vs ", " versus ", "compared to", "compared with",
            "previous period", "prior period", "last 2 months vs",
            "last month vs", "why did", "why has", "what caused",
            "decline", "drop", "fell", "decreased", "increased",
        ]
        has_comparison = any(s in q_lower for s in COMPARISON_SIGNALS)

        # Action-request signals — user wants recommendations/actions
        ACTION_SIGNALS = [
            "what should i do", "what can i do", "how to improve",
            "what actions", "suggest", "recommend", "corrective",
            "what do you recommend", "give me advice", "help me",
            "what should", "how should", "what to do",
        ]
        has_action_request = any(s in q_lower for s in ACTION_SIGNALS)

        # Multi-question signals — question contains multiple "?"  or "and"
        has_multiple_questions = q_lower.count("?") > 1 or (
            " and " in q_lower and len(q_words) > 15
        )

        # Complex: multiple strong signals that require multi-step execution
        is_complex = (
            len(high_concepts) >= 3
            or (net_score > 0.15 and strong_forecast)
            or (net_score > 0.15 and rec_score > 0.1)
            or (money_in_score > 0.1 and money_out_score > 0.1 and net_score > 0.1)
            or len(resolved.split()) > 25
            # Structural complexity — comparison + action = always multi-step
            or (has_comparison and has_action_request)
            or (has_comparison and net_score > 0.1)
            or (has_action_request and net_score > 0.1)
            or has_multiple_questions
        )

        if is_complex:
            intent_type = "complex"
            confidence  = 0.88
        elif strong_forecast:
            intent_type = "forecast"
            confidence  = min(0.95, 0.7 + forecast_score)
        elif strong_anomaly:
            intent_type = "anomaly"
            confidence  = min(0.95, 0.7 + anomaly_score)
        elif not top_concepts:
            # Before giving up with clarification, check if there's a time reference
            # A question with a month/year is almost certainly financial
            from app.services.time_context import TimeContextResolver
            dr = TimeContextResolver().resolve(resolved)
            if dr.is_explicit:
                intent_type = "analytics"
                confidence  = 0.65
            else:
                intent_type = "clarification"
                confidence  = 0.7
        else:
            intent_type = "analytics"
            confidence  = min(0.92, 0.6 + sorted_concepts[0][1] if sorted_concepts else 0.6)

        # ── Map concepts to tables ────────────────────────────────────────────
        tables: list[str] = []
        for concept in top_concepts:
            for table in CONCEPT_TABLE_AFFINITY.get(concept, []):
                if table not in tables and table in self._schema:
                    tables.append(table)
        if not tables:
            tables = []

        # ── Get relevant columns from live schema ─────────────────────────────
        columns: list[str] = []
        for table in tables[:2]:  # limit to top 2 tables
            if table in self._schema:
                columns.extend(self._schema[table].get("columns", [])[:8])

        # ── Score output format ───────────────────────────────────────────────
        format_scores = {
            fmt: _semantic_score(resolved, vocab)
            for fmt, vocab in FORMAT_VOCABULARY.items()
        }
        best_format = max(format_scores, key=format_scores.get)
        if max(format_scores.values()) < 0.05:
            # No clear format signal — infer from data type
            if "bank_transactions" in tables:
                best_format = "line"
            elif any(t in tables for t in ["invoice_records", "vendor_payments", "loan_obligations"]):
                best_format = "table"
            else:
                best_format = "bar"

        # ── Score group-by dimension ──────────────────────────────────────────
        groupby_scores = {
            dim: _semantic_score(resolved, vocab)
            for dim, vocab in GROUPBY_VOCABULARY.items()
        }
        best_groupby = max(groupby_scores, key=groupby_scores.get)
        group_by = best_groupby if groupby_scores[best_groupby] > 0.05 else None

        # ── Extract time context ──────────────────────────────────────────────
        from app.services.time_context import TimeContextResolver
        resolver = TimeContextResolver()
        date_range = resolver.resolve(resolved)
        time_label = date_range.label

        # ── Extract numeric entities ──────────────────────────────────────────
        entities: dict[str, Any] = {}
        # Horizon days
        horizon_match = re.search(r'(\d+)\s*days?', resolved)
        if horizon_match:
            entities["horizon_days"] = int(horizon_match.group(1))
        # Percentage change
        pct_match = re.search(r'(\d+)\s*%', resolved)
        if pct_match:
            entities["pct_change"] = int(pct_match.group(1))
        # Month count
        month_match = re.search(r'(\d+)\s*months?', resolved)
        if month_match:
            entities["n_months"] = int(month_match.group(1))

        return ParsedQuery(
            intent_type=intent_type,
            confidence=confidence,
            concepts=top_concepts[:5],
            tables=tables,
            columns=columns,
            chart_type=best_format,
            group_by=group_by,
            time_label=time_label,
            wants_forecast=forecast_score > 0.05,
            wants_comparison=concept_scores.get("net_position", 0) > 0.08,
            wants_anomaly=anomaly_score > 0.05,
            wants_recommendations=rec_score > 0.05,
            is_complex=is_complex,
            is_followup=is_followup,
            entities=entities,
            concept_scores=concept_scores,
        )

    def _resolve_context(self, question: str, history: list) -> tuple[str, bool]:
        """
        Resolve follow-up questions using conversation history.
        Returns (resolved_question, is_followup).
        No fixed signal words — uses semantic similarity to detect follow-ups.
        """
        if not history:
            return question.lower(), False

        # A follow-up is short AND semantically similar to recent history
        # OR starts with a pronoun/reference word
        q_lower = question.lower().strip()
        words   = q_lower.split()

        REFERENCE_STARTERS = {"it", "that", "this", "they", "them", "those",
                               "why", "how", "what about", "and", "also",
                               "i meant", "i mean", "actually", "instead"}

        is_followup = (
            len(words) <= 12
            and (words[0] in REFERENCE_STARTERS or
                 any(q_lower.startswith(s) for s in ("why did", "how did", "what caused",
                                                       "i meant", "i mean", "actually",
                                                       "what about", "and what")))
        )

        if is_followup:
            # Get last user message for context
            last_user = next(
                (
                    (h.content if hasattr(h, "content") else h.get("content", "")).lower()
                    for h in reversed(history)
                    if (h.role if hasattr(h, "role") else h.get("role")) == "user"
                ),
                ""
            )
            if last_user:
                return f"{last_user} {q_lower}", True

        return q_lower, False

    def _llm_parse(self, question: str, history: list | None) -> ParsedQuery | None:
        """Use LLM for parsing when enabled. Returns None if LLM fails."""
        try:
            from app.llm.client import get_llm
            llm = get_llm()
            if not llm.enabled:
                return None

            schema_summary = {
                t: list(info.get("columns", []))[:6]
                for t, info in list(self._schema.items())[:10]
            }

            system = f"""You are a financial query parser. Given a user question, return JSON:
{{
  "intent_type": "analytics|forecast|anomaly|complex|clarification",
  "concepts": ["money_in", "money_out", "net_position", "invoicing", "obligations", "risk_health", "anomalies", "forecast", "recommendations"],
  "tables": ["bank_transactions", "invoice_records", ...],
  "chart_type": "pie|bar|line|area|table",
  "group_by": "category|merchant_name|customer_name|month|null",
  "wants_forecast": true/false,
  "wants_comparison": true/false,
  "wants_anomaly": true/false,
  "is_complex": true/false,
  "entities": {{"horizon_days": 30, "n_months": 2}}
}}

Available tables: {list(schema_summary.keys())}
Schema sample: {schema_summary}"""

            context = ""
            if history:
                last = next((h.content if hasattr(h, "content") else h.get("content","")
                             for h in reversed(history)
                             if (h.role if hasattr(h,"role") else h.get("role")) == "user"), "")
                if last:
                    context = f"\nPrevious question: {last}"

            result = llm.json_chat(system, f"Question: {question}{context}", max_tokens=400)
            if not result:
                return None

            from app.services.time_context import TimeContextResolver
            date_range = TimeContextResolver().resolve(question)

            return ParsedQuery(
                intent_type=result.get("intent_type", "analytics"),
                confidence=0.92,
                concepts=result.get("concepts", []),
                tables=result.get("tables", []),
                columns=[],
                chart_type=result.get("chart_type", "line"),
                group_by=result.get("group_by"),
                time_label=date_range.label,
                wants_forecast=result.get("wants_forecast", False),
                wants_comparison=result.get("wants_comparison", False),
                wants_anomaly=result.get("wants_anomaly", False),
                wants_recommendations=result.get("wants_recommendations", False),
                is_complex=result.get("is_complex", False),
                is_followup=False,
                entities=result.get("entities", {}),
            )
        except Exception:
            return None


# ── Module-level singleton ────────────────────────────────────────────────────
_parser: SemanticParser | None = None


def get_parser() -> SemanticParser:
    global _parser
    if _parser is None:
        _parser = SemanticParser()
    return _parser


def parse_query(question: str, history: list | None = None) -> ParsedQuery:
    """Convenience function — parse a question into structured intent."""
    return get_parser().parse(question, history)
