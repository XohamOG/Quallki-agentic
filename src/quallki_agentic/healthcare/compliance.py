from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


SOURCES = {
    "hipaa_security": "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C",
    "hipaa_breach": "https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html",
    "nist_csf": "https://www.nist.gov/cyberframework",
    "nist_ir": "https://csrc.nist.gov/pubs/sp/800/61/r3/final",
    "nist_800_66": "https://csrc.nist.gov/pubs/sp/800/66/r2/final",
    "gdpr": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
    "iso_27001": "https://www.iso.org/standard/27001.html",
    "soc2": "https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria",
    "nis2": "https://eur-lex.europa.eu/eli/dir/2022/2555/oj",
}


CONTROL_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "HIPAA-164.308(a)(1)",
        "framework": "HIPAA Security Rule",
        "control": "Security management process: risk analysis, risk management, sanctions, and activity review.",
        "source_url": SOURCES["hipaa_security"],
        "applicability": "hipaa_applicable",
        "owner": "Security and Privacy Officer",
        "required_evidence": ("risk_analysis", "risk_treatment", "activity_review", "incident_record"),
        "factors": ("policy_approved", "owner_assigned", "source_system", "event_time", "integrity_hash"),
    },
    {
        "id": "HIPAA-164.308(a)(6)",
        "framework": "HIPAA Security Rule",
        "control": "Security incident procedures: identify, respond, mitigate, and document outcomes.",
        "source_url": SOURCES["hipaa_security"],
        "applicability": "hipaa_applicable",
        "owner": "Incident Response Lead",
        "required_evidence": ("incident_ticket", "timeline", "containment_record", "outcome_record"),
        "factors": ("ticket_id", "approver", "execution_time", "source_system", "integrity_hash"),
    },
    {
        "id": "HIPAA-164.312(b)",
        "framework": "HIPAA Security Rule",
        "control": "Audit controls: mechanisms that record and examine activity in systems containing ePHI.",
        "source_url": SOURCES["hipaa_security"],
        "applicability": "hipaa_applicable",
        "owner": "Security Operations",
        "required_evidence": ("audit_log_sample", "log_source_inventory", "retention_policy", "review_record"),
        "factors": ("source_system", "event_time", "integrity_hash", "retention_days"),
    },
    {
        "id": "HIPAA-164.316",
        "framework": "HIPAA Security Rule",
        "control": "Policies, procedures, documentation, retention, availability, and periodic updates.",
        "source_url": SOURCES["hipaa_security"],
        "applicability": "hipaa_applicable",
        "owner": "Compliance and Security Officer",
        "required_evidence": ("policy_document", "procedure_document", "review_record", "retention_record"),
        "factors": ("policy_approved", "owner_assigned", "last_reviewed", "retention_days"),
    },
    {
        "id": "NIST-CSF-2.0-RS.MA",
        "framework": "NIST CSF 2.0",
        "control": "Respond: incident management and response activities are coordinated and recorded.",
        "source_url": SOURCES["nist_csf"],
        "applicability": "always",
        "owner": "Incident Response Lead",
        "required_evidence": ("incident_ticket", "triage_record", "response_record", "lessons_learned"),
        "factors": ("ticket_id", "approver", "execution_time", "source_system"),
    },
    {
        "id": "NIST-SP-800-61r3",
        "framework": "NIST SP 800-61 Rev. 3",
        "control": "Incident response lifecycle and integration with cybersecurity risk management.",
        "source_url": SOURCES["nist_ir"],
        "applicability": "always",
        "owner": "Incident Response Lead",
        "required_evidence": ("incident_plan", "incident_ticket", "timeline", "after_action_report"),
        "factors": ("policy_approved", "owner_assigned", "last_reviewed", "integrity_hash"),
    },
    {
        "id": "GDPR-ART32",
        "framework": "GDPR Article 32",
        "control": "Risk-appropriate technical and organisational security measures.",
        "source_url": SOURCES["gdpr"],
        "applicability": "gdpr_applicable",
        "owner": "Data Protection Officer",
        "required_evidence": ("security_risk_assessment", "technical_measures", "organisational_measures", "effectiveness_test"),
        "factors": ("policy_approved", "owner_assigned", "last_reviewed", "source_system"),
    },
    {
        "id": "GDPR-ART33",
        "framework": "GDPR Article 33",
        "control": "Personal-data breach assessment, documentation, and supervisory-authority notification where required.",
        "source_url": SOURCES["gdpr"],
        "applicability": "gdpr_applicable",
        "owner": "Data Protection Officer",
        "required_evidence": ("breach_assessment", "notification_decision", "notification_clock", "notification_record"),
        "factors": ("approver", "decision_time", "affected_records", "data_categories"),
    },
    {
        "id": "NIST-SP-800-66r2",
        "framework": "NIST SP 800-66 Rev. 2",
        "control": "HIPAA Security Rule implementation guidance and safeguard risk assessment.",
        "source_url": SOURCES["nist_800_66"],
        "applicability": "hipaa_applicable",
        "owner": "Privacy and Security Officers",
        "required_evidence": ("risk_analysis", "phi_inventory", "safeguards_assessment", "corrective_action_plan"),
        "factors": ("policy_approved", "owner_assigned", "last_reviewed"),
    },
    {
        "id": "ISO-27001-INCIDENT",
        "framework": "ISO/IEC 27001:2022",
        "control": "ISMS incident-management, corrective action, internal audit, and management review evidence.",
        "source_url": SOURCES["iso_27001"],
        "applicability": "iso_scope",
        "owner": "ISMS Manager",
        "required_evidence": ("isms_scope", "incident_record", "corrective_action", "internal_audit", "management_review"),
        "factors": ("policy_approved", "owner_assigned", "last_reviewed", "auditor_reference"),
    },
    {
        "id": "SOC2-CC7",
        "framework": "AICPA SOC 2 Trust Services Criteria",
        "control": "CC7: System operations, monitoring, anomaly detection, and incident response.",
        "source_url": SOURCES["soc2"],
        "applicability": "soc2_scope",
        "owner": "Control Owner and SOC 2 Auditor",
        "required_evidence": ("control_description", "monitoring_alerts", "ticket_samples", "change_samples", "auditor_testing"),
        "factors": ("population_period", "sample_method", "approver", "auditor_reference"),
    },
    {
        "id": "NIS2-ART21-23",
        "framework": "EU NIS2 Directive",
        "control": "Risk-management measures, incident handling, and 24-hour/72-hour/final reporting workflow.",
        "source_url": SOURCES["nis2"],
        "applicability": "nis2_applicable",
        "owner": "Legal, Risk, and Incident Response",
        "required_evidence": ("entity_scope_decision", "risk_management_policy", "incident_classification", "early_warning", "incident_notification", "final_report"),
        "factors": ("management_approval", "decision_time", "notification_time", "cross_border_impact"),
    },
)


def healthcare_soc_checklist() -> list[dict[str, Any]]:
    return [dict(item) for item in CONTROL_CATALOG]


def _is_applicable(item: dict[str, Any], context: dict[str, Any]) -> bool:
    key = item["applicability"]
    return key == "always" or bool(context.get(key, False))


def _present(evidence: dict[str, Any], key: str) -> bool:
    value = evidence.get(key)
    if isinstance(value, bool):
        return value
    return value not in (None, "", [], {})


def assess_compliance(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
    """Assess SIEM evidence completeness; never determine legal compliance."""
    context = payload.get("compliance_context", {})
    context = context if isinstance(context, dict) else {}
    evidence_map = payload.get("compliance_evidence", {})
    evidence_map = evidence_map if isinstance(evidence_map, dict) else {}
    now = datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []

    for item in CONTROL_CATALOG:
        evidence = evidence_map.get(item["id"], {})
        evidence = evidence if isinstance(evidence, dict) else {}
        applicable = _is_applicable(item, context)
        required = list(item["required_evidence"])
        present = [key for key in required if _present(evidence, key)]
        missing = [key for key in required if key not in present]
        factor_values = {key: _present(evidence, key) for key in item["factors"]}
        factor_values["fresh_enough"] = bool(evidence.get("event_time"))
        factor_values["integrity_verified"] = bool(evidence.get("integrity_hash"))
        if not applicable:
            status = "not_applicable"
        elif not present:
            status = "not_evidenced"
        elif missing:
            status = "partial"
        else:
            status = "evidence_complete"
        rows.append({
            **item,
            "applicable": applicable,
            "status": status,
            "evidence_present": present,
            "evidence_missing": missing,
            "quality_factors": factor_values,
            "evidence_source": evidence.get("source_system", "not_supplied"),
            "last_evidence_time": evidence.get("event_time", "not_supplied"),
            "review_required": status in {"partial", "evidence_complete"},
            "assurance_note": "Evidence assessment only; a qualified control owner, privacy/legal reviewer, or independent auditor must determine compliance.",
        })

    applicable_rows = [row for row in rows if row["applicable"]]
    complete = sum(row["status"] == "evidence_complete" for row in applicable_rows)
    partial = sum(row["status"] == "partial" for row in applicable_rows)
    context_quality = {
        "assessment_time": now.isoformat(),
        "applicability_context_supplied": bool(context),
        "evidence_records_supplied": len(evidence_map),
        "applicable_controls": len(applicable_rows),
        "evidence_complete": complete,
        "partial": partial,
        "not_evidenced": sum(row["status"] == "not_evidenced" for row in applicable_rows),
        "not_applicable": len(rows) - len(applicable_rows),
        "compliance_determination": "not_made",
    }
    summary = (
        f"SIEM evidence assessment: {complete}/{len(applicable_rows)} applicable controls have complete declared evidence; "
        f"{partial} partial and {context_quality['not_evidenced']} not evidenced. "
        "No legal, regulatory, certification, or attestation determination was made."
    )
    return rows, summary, context_quality


def summarize_checklist(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    rows, summary, _ = assess_compliance(payload)
    return rows, summary
