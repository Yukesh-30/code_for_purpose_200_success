from __future__ import annotations

from dataclasses import dataclass

from app.semantic.definitions import MetricDefinition, find_metrics
from app.semantic.vector_store import SemanticDocument, SemanticVectorStore


@dataclass(frozen=True)
class SemanticMapping:
    metrics: list[MetricDefinition]
    documents: list[SemanticDocument]
    uses_current_neon_schema: bool = True


class SemanticRetriever:
    def __init__(self, vector_store: SemanticVectorStore | None = None) -> None:
        self.vector_store = vector_store or SemanticVectorStore()

    def map_question(self, question: str) -> SemanticMapping:
        return SemanticMapping(metrics=find_metrics(question), documents=self.vector_store.search(question))
