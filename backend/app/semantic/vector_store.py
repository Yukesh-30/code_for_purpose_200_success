from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from app.core.config import Settings, get_settings
from app.semantic.definitions import CANONICAL_SCHEMA, CURRENT_NEON_SCHEMA, METRICS


@dataclass(frozen=True)
class SemanticDocument:
    id: str
    text: str
    metadata: dict[str, Any]


TOKEN_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]+")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


class SemanticVectorStore:
    """Chroma-backed semantic store with deterministic local retrieval fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._documents = build_default_documents()
        self._collection: Any | None = None
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        except ImportError:
            return
        try:
            # Use a lightweight embedding function that avoids downloading ONNX models
            # by using a simple hash-based approach for local/dev environments
            from chromadb.utils.embedding_functions import EmbeddingFunction
            import hashlib

            class FastHashEmbedding(EmbeddingFunction):
                """Deterministic hash-based embedding — no model download required."""
                DIM = 64

                def __call__(self, input):  # noqa: A002
                    results = []
                    for text in input:
                        h = hashlib.sha256(text.encode()).digest()
                        vec = [(b / 255.0) * 2 - 1 for b in h[:self.DIM]]
                        results.append(vec)
                    return results

            client = chromadb.PersistentClient(path=self.settings.vector_store_path)
            self._collection = client.get_or_create_collection(
                self.settings.vector_collection_name,
                embedding_function=FastHashEmbedding(),
            )
            if self._collection.count():
                return
            self._collection.add(
                ids=[doc.id for doc in self._documents],
                documents=[doc.text for doc in self._documents],
                metadatas=[doc.metadata for doc in self._documents],
            )
        except Exception:
            # Fall back to local token-based retrieval if Chroma fails
            self._collection = None

    def search(self, query: str, limit: int = 6) -> list[SemanticDocument]:
        if self._collection is not None:
            result = self._collection.query(query_texts=[query], n_results=limit)
            return [
                SemanticDocument(id=str(doc_id), text=text, metadata=dict(metadata or {}))
                for doc_id, text, metadata in zip(
                    result.get("ids", [[]])[0],
                    result.get("documents", [[]])[0],
                    result.get("metadatas", [[]])[0],
                )
            ]

        query_tokens = _tokens(query)
        scored: list[tuple[float, SemanticDocument]] = []
        for doc in self._documents:
            doc_tokens = _tokens(doc.text)
            overlap = len(query_tokens & doc_tokens)
            score = overlap / math.sqrt(max(len(doc_tokens), 1))
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:limit]]


def build_default_documents() -> list[SemanticDocument]:
    documents: list[SemanticDocument] = []
    for metric in METRICS.values():
        documents.append(
            SemanticDocument(
                id=f"metric:{metric.name}",
                text=f"{metric.name}: {metric.description} Formula: {metric.expression}. Synonyms: {', '.join(metric.synonyms)}.",
                metadata={"kind": "metric", "metric": metric.name, "table": metric.current_table or metric.canonical_table},
            )
        )
    for table, columns in CANONICAL_SCHEMA.items():
        documents.append(SemanticDocument(id=f"table:{table}", text=f"Canonical table {table} columns: {', '.join(sorted(columns))}.", metadata={"kind": "table", "table": table}))
    for table, columns in CURRENT_NEON_SCHEMA.items():
        documents.append(SemanticDocument(id=f"current-table:{table}", text=f"Current Neon table {table} columns: {', '.join(sorted(columns))}.", metadata={"kind": "current_table", "table": table}))
    documents.extend(
        [
            SemanticDocument(id="example:cashflow_last_month", text="Question: What was my cashflow last month? Use inflow minus outflow by transaction date.", metadata={"kind": "example", "intent": "cashflow"}),
            SemanticDocument(id="example:why_drop", text="Question: Why did cashflow drop? Compare current and prior period revenue and expense drivers.", metadata={"kind": "example", "intent": "driver_analysis"}),
            SemanticDocument(id="example:forecast", text="Question: Predict cashflow next month. Use daily inflow and outflow history plus committed payments.", metadata={"kind": "example", "intent": "forecast"}),
        ]
    )
    return documents
