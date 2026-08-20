from __future__ import annotations

from typing import TypedDict


class OrchestratorState(TypedDict, total=False):
    message: str
    source_ip: str
    scenario: str
    asset_type: str
    contains_phi: bool
    clinical_impact: str
    compliance_context: dict
    compliance_evidence: dict
    alert_id: str
    event_time: str
    qml_label: str
    iocs: list[str]

    alert_object: dict
    triage_result: dict
    threat_intel_result: dict
    route: str
    assignments: list[dict]
    response_actions: list[str]
    forensics_summary: str
    compliance_note: str
    compliance_checklist: list[dict]
    compliance_assessment: dict
    final_summary: str
