from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from quallki_agentic.orchestrator.edges import route_after_triage
from quallki_agentic.orchestrator.nodes import (
    auto_close_node,
    compliance_node,
    detection_node,
    finalize_node,
    forensics_node,
    response_node,
    threat_intel_node,
    triage_node,
)
from quallki_agentic.orchestrator.state import OrchestratorState


def build_orchestrator_graph():
    workflow = StateGraph(OrchestratorState)

    workflow.add_node("detection", detection_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("threat_intel", threat_intel_node)
    workflow.add_node("response", response_node)
    workflow.add_node("forensics", forensics_node)
    workflow.add_node("auto_close", auto_close_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("finalize", finalize_node)

    workflow.add_edge(START, "detection")
    workflow.add_edge("detection", "triage")
    workflow.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "response_path": "threat_intel",
            "investigate_path": "threat_intel",
            "auto_close": "auto_close",
        },
    )
    workflow.add_edge("threat_intel", "response")
    workflow.add_edge("response", "forensics")
    workflow.add_edge("forensics", "compliance")
    workflow.add_edge("compliance", "finalize")
    workflow.add_edge("auto_close", END)
    workflow.add_edge("finalize", END)

    return workflow.compile()
