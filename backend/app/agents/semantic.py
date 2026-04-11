from __future__ import annotations

from app.agents.state import AgentState
from app.semantic.retriever import SemanticRetriever
from app.services.time_context import TimeContextResolver


class SemanticAgent:
    def __init__(self, retriever: SemanticRetriever | None = None, time_resolver: TimeContextResolver | None = None) -> None:
        self.retriever = retriever or SemanticRetriever()
        self.time_resolver = time_resolver or TimeContextResolver()

    def map(self, state: AgentState) -> AgentState:
        state["semantic_mapping"] = self.retriever.map_question(state["question"])
        state["date_range"] = self.time_resolver.resolve(state["question"], state.get("as_of_date"))
        return state
