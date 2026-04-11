from functools import lru_cache

from app.agents.graph import FinancialIntelligenceGraph
from app.core.config import get_settings
from app.services.query_executor import QueryExecutor

_graph: FinancialIntelligenceGraph | None = None


def get_graph() -> FinancialIntelligenceGraph:
    """Return singleton graph — recreated on each process start (no lru_cache)."""
    global _graph
    if _graph is None:
        settings = get_settings()
        executor = QueryExecutor(max_rows=settings.max_result_rows)
        _graph = FinancialIntelligenceGraph(executor=executor, settings=settings)
    return _graph
