from __future__ import annotations

from quallki_agentic.config import Settings
from quallki_agentic.agents import (
    ComplianceAgent,
    DetectionAgent,
    ForensicsAgent,
    ResponseAgent,
    ThreatIntelAgent,
    TriageAgent,
)
from quallki_agentic.messaging import build_message_bus
from quallki_agentic.orchestrator.schema import TaskAssignment, now_iso
from quallki_agentic.orchestrator.state import OrchestratorState


detection_agent = DetectionAgent()
triage_agent = TriageAgent()
threat_intel_agent = ThreatIntelAgent()
response_agent = ResponseAgent()
forensics_agent = ForensicsAgent()
compliance_agent = ComplianceAgent()
settings = Settings.from_env()
message_bus = build_message_bus(settings)


def _publish(topic: str, event: dict[str, object]) -> None:
    if not settings.enable_event_bus:
        return
    try:
        message_bus.publish(topic, event)
    except Exception:
        return


def detection_node(state: OrchestratorState) -> OrchestratorState:
    result = detection_agent.run(state)
    _publish(
        "agent.detection.completed",
        {
            "alert_id": result.get("alert_object", {}).get("alert_id") if isinstance(result.get("alert_object"), dict) else "auto",
            "iocs_count": len(result.get("iocs", [])) if isinstance(result.get("iocs"), list) else 0,
        },
    )
    return result


def triage_node(state: OrchestratorState) -> OrchestratorState:
    result = triage_agent.run(state)
    route = result.get("route", "auto_close")
    _publish("agent.triage.completed", {"route": route, "triage": result.get("triage_result", {})})
    return result


def threat_intel_node(state: OrchestratorState) -> OrchestratorState:
    result = threat_intel_agent.run(state)
    _publish("agent.threat_intel.completed", {"threat_intel": result.get("threat_intel_result", {})})
    return result


def response_node(state: OrchestratorState) -> OrchestratorState:
    assignment = TaskAssignment(
        task_id=f"task-response-{state.get('alert_id', 'auto')}",
        target_agent="response",
        reason="Priority route requires containment",
        created_at=now_iso(),
    )
    result = response_agent.run(state)
    assignments = [assignment.__dict__]
    _publish("agent.response.completed", {"assignments": assignments, "actions": result.get("response_actions", [])})
    return {"assignments": assignments, **result}


def forensics_node(state: OrchestratorState) -> OrchestratorState:
    result = forensics_agent.run(state)
    _publish("agent.forensics.completed", {"summary": result.get("forensics_summary", "")})
    return result


def auto_close_node(state: OrchestratorState) -> OrchestratorState:
    triage_result = state.get("triage_result", {})
    reason = "Low-risk event auto-closed with audit trail."
    if isinstance(triage_result, dict):
        reason = f"Auto-closed: {triage_result.get('reasoning', reason)}"
    result = {"final_summary": reason}
    _publish("agent.orchestrator.auto_closed", result)
    return result


def compliance_node(state: OrchestratorState) -> OrchestratorState:
    result = compliance_agent.run(state)
    _publish("agent.compliance.completed", result)
    return result


def finalize_node(state: OrchestratorState) -> OrchestratorState:
    triage = state.get("triage_result", {})
    threat = state.get("threat_intel_result", {})
    actions = state.get("response_actions", [])
    forensics = state.get("forensics_summary", "")
    compliance = state.get("compliance_note", "")

    priority = "P4"
    reasoning = "n/a"
    if isinstance(triage, dict):
        priority = str(triage.get("priority", "P4"))
        reasoning = str(triage.get("reasoning", "n/a"))

    techniques = []
    if isinstance(threat, dict):
        raw = threat.get("attack_techniques", [])
        if isinstance(raw, list):
            techniques = [str(v) for v in raw]

    action_text = "; ".join(actions) if isinstance(actions, list) and actions else "No containment action executed."
    summary = (
        f"Priority: {priority}. "
        f"Reasoning: {reasoning}. "
        f"ATT&CK: {', '.join(techniques) if techniques else 'none'}. "
        f"Actions: {action_text} "
        f"Forensics: {forensics if forensics else 'pending'}. "
        f"Compliance: {compliance if compliance else 'queued'}."
    )
    result = {"final_summary": summary}
    _publish("agent.orchestrator.finalized", result)
    return result
