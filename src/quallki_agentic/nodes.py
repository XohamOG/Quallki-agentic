from __future__ import annotations

from quallki_agentic.knowledge import LocalKnowledgeBase
from quallki_agentic.providers import AlertClassifier, IncidentResponder
from quallki_agentic.state import AgentState


def ingest_alert_node(state: AgentState) -> AgentState:
    raw_message = state.get("message", "")
    normalized = " ".join(raw_message.split())
    return {"normalized_alert": normalized}


def classify_alert_node(state: AgentState, classifier: AlertClassifier) -> AgentState:
    alert = state.get("normalized_alert", state.get("message", ""))
    classification = classifier.classify(alert)
    return {
        "classification_label": classification.label,
        "severity": classification.severity,
        "confidence": classification.confidence,
    }


def retrieve_context_node(state: AgentState, knowledge_base: LocalKnowledgeBase) -> AgentState:
    alert = state.get("normalized_alert", state.get("message", ""))
    snippets = knowledge_base.search(alert)
    return {"context_snippets": snippets}


def recommend_actions_node(state: AgentState) -> AgentState:
    severity = state.get("severity", "low")
    mapping = {
        "critical": [
            "Isolate host from network immediately.",
            "Escalate to incident commander and activate severity-1 runbook.",
            "Collect volatile artifacts before system restart.",
        ],
        "high": [
            "Restrict suspicious accounts and enforce MFA checks.",
            "Validate lateral movement indicators in EDR and SIEM.",
            "Preserve relevant logs for 72 hours and open incident ticket.",
        ],
        "medium": [
            "Increase monitoring for correlated events.",
            "Verify baseline deviations on source host.",
            "Tag event for analyst review in queue.",
        ],
    }
    actions = mapping.get(severity, ["Queue event for routine triage and enrichment."])
    return {"recommended_actions": actions}


def generate_response_node(state: AgentState, responder: IncidentResponder) -> AgentState:
    from quallki_agentic.state import ClassificationResult

    alert = state.get("normalized_alert", state.get("message", ""))
    classification = ClassificationResult(
        label=state.get("classification_label", "unknown"),
        severity=state.get("severity", "low"),
        confidence=float(state.get("confidence", 0.5)),
    )
    response = responder.respond(
        alert=alert,
        classification=classification,
        context_snippets=state.get("context_snippets", []),
    )
    return {"response": response}
