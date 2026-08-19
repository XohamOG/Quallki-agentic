from __future__ import annotations

from typing import Any


def healthcare_soc_checklist() -> list[dict[str, str]]:
    return [
        {
            "id": "HC-01",
            "framework": "HIPAA Security Rule",
            "control": "164.308(a)(1) Security incident procedures",
            "evidence_key": "incident_ticket",
        },
        {
            "id": "HC-02",
            "framework": "HIPAA Security Rule",
            "control": "164.312(b) Audit controls",
            "evidence_key": "audit_log_reference",
        },
        {
            "id": "HC-03",
            "framework": "HIPAA Security Rule",
            "control": "164.312(a) Access control and emergency access",
            "evidence_key": "access_revocation_record",
        },
        {
            "id": "HC-04",
            "framework": "NIST CSF 2.0",
            "control": "RS.MA Mitigation actions executed",
            "evidence_key": "containment_actions",
        },
        {
            "id": "HC-05",
            "framework": "NIST SP 800-66",
            "control": "PHI breach assessment and documentation",
            "evidence_key": "phi_impact_assessment",
        },
        {
            "id": "HC-06",
            "framework": "GDPR Article 32",
            "control": "Security of processing and risk-based technical controls",
            "evidence_key": "gdpr_security_controls",
        },
        {
            "id": "HC-07",
            "framework": "GDPR Article 33",
            "control": "Breach notification workflow prepared within required timeline",
            "evidence_key": "gdpr_breach_notification",
        },
        {
            "id": "HC-08",
            "framework": "ISO/IEC 27001:2022",
            "control": "Incident response and lessons-learned record",
            "evidence_key": "iso27001_incident_record",
        },
        {
            "id": "HC-09",
            "framework": "SOC 2 CC7",
            "control": "Change management and incident containment evidence",
            "evidence_key": "soc2_change_evidence",
        },
        {
            "id": "HC-10",
            "framework": "NIS2",
            "control": "Essential service cybersecurity event reporting preparedness",
            "evidence_key": "nis2_reporting_readiness",
        },
    ]


def summarize_checklist(payload: dict[str, Any]) -> tuple[list[dict[str, str]], str]:
    triage = payload.get("triage_result", {})
    actions = payload.get("response_actions", [])
    alert = payload.get("alert_object", {})

    contains_phi = False
    if isinstance(alert, dict):
        contains_phi = bool(alert.get("contains_phi", False))

    priority = "P4"
    if isinstance(triage, dict):
        priority = str(triage.get("priority", "P4"))

    completed_keys = {
        "incident_ticket",
        "audit_log_reference",
        "gdpr_security_controls",
        "iso27001_incident_record",
        "soc2_change_evidence",
        "nis2_reporting_readiness",
    }
    if isinstance(actions, list) and actions:
        completed_keys.add("containment_actions")
        completed_keys.add("access_revocation_record")
        completed_keys.add("gdpr_breach_notification")
    if contains_phi:
        completed_keys.add("phi_impact_assessment")

    rows: list[dict[str, str]] = []
    for item in healthcare_soc_checklist():
        status = "done" if item["evidence_key"] in completed_keys else "pending"
        row = {
            "id": item["id"],
            "framework": item["framework"],
            "control": item["control"],
            "status": status,
        }
        rows.append(row)

    done_count = sum(1 for row in rows if row["status"] == "done")
    summary = (
        f"Healthcare SOC compliance coverage: {done_count}/{len(rows)} controls done "
        f"across HIPAA, GDPR, ISO 27001, SOC 2, NIS2, and NIST guidance. "
        f"Incident priority: {priority}. "
        f"PHI impact assessment: {'included' if contains_phi else 'not required in this event'}"
    )
    return rows, summary
