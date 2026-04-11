from __future__ import annotations

from app.agents.sql_validator import SQLValidator
from app.semantic.retriever import SemanticRetriever


def build_langchain_tools(retriever: SemanticRetriever | None = None, validator: SQLValidator | None = None):
    """Expose safe deterministic capabilities as LangChain tools when installed."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError:
        return []

    retriever = retriever or SemanticRetriever()
    validator = validator or SQLValidator()

    def semantic_search(query: str) -> list[dict]:
        mapping = retriever.map_question(query)
        return [
            {"id": document.id, "text": document.text, "metadata": document.metadata}
            for document in mapping.documents
        ]

    def validate_sql(sql: str, business_id: int) -> dict:
        result = validator.validate(sql, business_id=business_id)
        return {"ok": result.ok, "sql": result.sql, "error": result.error}

    return [
        StructuredTool.from_function(
            func=semantic_search,
            name="financial_semantic_search",
            description="Retrieve trusted financial metric definitions, column meanings, and query examples.",
        ),
        StructuredTool.from_function(
            func=validate_sql,
            name="validate_read_only_financial_sql",
            description="Validate that SQL is read-only, schema-safe, and scoped to the requested business.",
        ),
    ]
