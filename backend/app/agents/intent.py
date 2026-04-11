from __future__ import annotations

import re

from app.agents.state import AgentState, IntentResult
from app.agents.semantic_parser import parse_query, ParsedQuery

# ── SQL injection detection — structural, not semantic ────────────────────────
# These are database operation patterns that must never reach the executor.
# This is NOT a keyword list — it's a structural grammar check.
_SQL_WRITE_PATTERNS = (
    r'\bdrop\s+table\b',
    r'\btruncate\s+table\b',
    r'\bdelete\s+from\b',
    r'\binsert\s+into\b',
    r'\bupdate\s+\w+\s+set\b',
    r'\balter\s+table\b',
    r'\bcreate\s+table\b',
    r'\bgrant\s+\w+\s+on\b',
    r'\brevoke\s+\w+\s+on\b',
    r'\bexec\s*\(',
    r'\bexecute\s*\(',
)


def _is_sql_write(text: str) -> bool:
    """Detect SQL write/destructive operations by grammar pattern."""
    t = text.lower()
    return any(re.search(p, t) for p in _SQL_WRITE_PATTERNS)


class IntentAgent:
    """
    Fully dynamic intent classifier.

    Decision flow:
    1. SQL injection check (grammar-based, not keyword-based)
    2. SemanticParser scores the question against the live DB schema
    3. If total financial relevance score is near zero → out_of_scope
    4. Otherwise map parsed result to intent type

    No hardcoded keyword lists. No regex for "what is 2+3".
    The semantic scorer handles everything — if a question has zero
    financial concept score, it's out of scope by definition.
    """

    # Minimum total concept score to be considered financial
    # Below this → the question has no financial meaning
    _MIN_FINANCIAL_SCORE = 0.05

    def classify(self, state: AgentState) -> AgentState:
        question = state["question"].strip()
        history  = state.get("history", [])

        # ── 1. SQL write/injection — structural check only ────────────────────
        if _is_sql_write(question):
            state["intent"] = {
                "intent":     "unsafe",
                "confidence": 0.99,
                "ambiguity":  "That looks like a database write operation — I only do read-only analytics.",
                "requires_sql": False,
                "is_complex":   False,
            }
            return state

        # ── 2. No business context ────────────────────────────────────────────
        if not state.get("business_id"):
            state["intent"] = {
                "intent":     "clarification",
                "confidence": 0.95,
                "ambiguity":  "Which business should I analyze?",
                "requires_sql": False,
                "is_complex":   False,
            }
            return state

        # ── 3. Semantic parsing — fully dynamic ───────────────────────────────
        parsed: ParsedQuery = parse_query(question, history)
        state["parsed_query"] = parsed

        # ── 4. Out-of-scope detection via semantic score ──────────────────────
        # Three tiers:
        # 1. Financial data query  → DB pipeline (score > threshold)
        # 2. General financial Q   → LLM answers conversationally (score > 0, no data needed)
        # 3. Truly off-topic       → polite redirect (score ≈ 0, no time, no history)
        total_financial_score = sum(parsed.concept_scores.values())
        has_explicit_time     = parsed.time_label not in ("unspecified",)
        has_history           = bool(history)

        # Tier 3: completely off-topic — zero financial relevance
        is_off_topic = (
            total_financial_score < self._MIN_FINANCIAL_SCORE
            and not has_history
            and (not has_explicit_time or parsed.time_label == "today")
        )

        if is_off_topic:
            state["intent"] = {
                "intent":     "out_of_scope",
                "confidence": round(1.0 - total_financial_score, 2),
                "ambiguity":  question,
                "requires_sql": False,
                "is_complex":   False,
            }
            return state

        # Tier 2: general financial question — no data needed, LLM can answer
        # Signals: no time reference, no specific entity, short question, conceptual
        is_conversational = (
            total_financial_score > 0
            and not has_explicit_time
            and not has_history
            and len(question.split()) <= 12
            and parsed.intent_type not in ("forecast", "anomaly", "complex")
            and not any(w in question.lower() for w in (
                "my ", "i ", "show", "list", "find", "detect",
                "what was", "how much", "how many", "last ", "this ",
            ))
        )

        if is_conversational:
            state["intent"] = {
                "intent":     "conversational",
                "confidence": 0.85,
                "ambiguity":  None,
                "requires_sql": False,
                "is_complex":   False,
                "question":   question,
            }
            return state

        # ── 5. Clarification — parsed but no actionable concepts ──────────────
        if parsed.intent_type == "clarification":
            state["intent"] = {
                "intent":     "clarification",
                "confidence": 0.75,
                "ambiguity":  "What would you like to know? Try asking about cashflow, invoices, expenses, or forecasts.",
                "requires_sql": False,
                "is_complex":   False,
            }
            return state

        # ── 6. Map to intent ──────────────────────────────────────────────────
        state["intent"] = {
            "intent":       parsed.intent_type,
            "confidence":   parsed.confidence,
            "ambiguity":    None,
            "requires_sql": True,
            "is_complex":   parsed.is_complex,
            "has_forecast": parsed.wants_forecast,
            "has_anomaly":  parsed.wants_anomaly,
            "tables":       parsed.tables,
            "chart_type":   parsed.chart_type,
            "group_by":     parsed.group_by,
            "concepts":     parsed.concepts,
            "entities":     parsed.entities,
        }
        return state
