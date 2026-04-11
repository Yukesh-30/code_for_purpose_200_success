from __future__ import annotations

from app.agents.state import AgentState


class SchemaSelector:
    """
    Dynamic schema context selector.
    Uses the ParsedQuery from SemanticParser — no fixed keyword maps.
    Falls back to intent-based selection if parsed_query is unavailable.
    """

    def select(self, state: AgentState) -> AgentState:
        parsed = state.get("parsed_query")
        intent = state.get("intent", {})

        # Load live schema
        from app.agents.semantic_parser import _load_live_schema
        live_schema = _load_live_schema()

        # Get tables from parsed query (dynamically determined)
        tables = parsed.tables if parsed and parsed.tables else intent.get("tables", [])

        # Build schema context from live schema — always current
        schema_context = {}
        for table in tables[:3]:  # limit to top 3 relevant tables
            if table in live_schema:
                schema_context[table] = live_schema[table].get("columns", [])

        if not schema_context:
            state["schema_error"] = "No validated schema context could be selected for this question."

        state["schema_context"] = schema_context
        return state
