from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from quallki_agentic.config import Settings
from quallki_agentic.knowledge import LocalKnowledgeBase
from quallki_agentic.nodes import (
    classify_alert_node,
    generate_response_node,
    ingest_alert_node,
    recommend_actions_node,
    retrieve_context_node,
)
from quallki_agentic.providers import build_classifier, build_responder
from quallki_agentic.state import AgentState


def build_graph(settings: Settings | None = None):
    runtime_settings = settings or Settings.from_env()
    classifier = build_classifier(runtime_settings)
    responder = build_responder(runtime_settings)
    knowledge_base = LocalKnowledgeBase(runtime_settings.knowledge_dir)

    workflow = StateGraph(AgentState)
    workflow.add_node("ingest", ingest_alert_node)
    workflow.add_node("classify", lambda state: classify_alert_node(state, classifier))
    workflow.add_node("retrieve", lambda state: retrieve_context_node(state, knowledge_base))
    workflow.add_node("recommend", recommend_actions_node)
    workflow.add_node("respond", lambda state: generate_response_node(state, responder))

    workflow.add_edge(START, "ingest")
    workflow.add_edge("ingest", "classify")
    workflow.add_edge("classify", "retrieve")
    workflow.add_edge("retrieve", "recommend")
    workflow.add_edge("recommend", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()
