# SIEM Compliance Evidence Checklist

This project implements a **SIEM evidence assessor**, not a legal compliance
certifier. It evaluates whether evidence records supplied by the SIEM/GRC
integrations are present, applicable, attributable, time-bound, and suitable
for human review.

## Status Model

- `not_applicable`: applicability context says the framework/control does not apply.
- `not_evidenced`: the control applies, but no required evidence was supplied.
- `partial`: some required evidence was supplied, but one or more required items are missing.
- `evidence_complete`: all declared required evidence fields are supplied; this still requires control-owner, privacy/legal, or independent-auditor review.

The system never returns `compliant`, `certified`, or `attested`.

## Official Sources

| Source | Use in this SIEM | Official document |
| --- | --- | --- |
| HIPAA Security Rule | Administrative, physical, technical safeguards; incident procedures; audit controls; documentation | [eCFR Title 45 Part 164 Subpart C](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C) |
| HHS HIPAA Breach Notification Rule | PHI breach risk assessment, notification decisions, documentation | [HHS Breach Notification Rule](https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html) |
| NIST CSF 2.0 | Risk governance and incident response outcome mapping | [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) |
| NIST SP 800-61 Rev. 3 | Incident response lifecycle and evidence expectations | [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) |
| NIST SP 800-66 Rev. 2 | HIPAA Security Rule implementation guidance | [NIST SP 800-66 Rev. 2](https://csrc.nist.gov/pubs/sp/800/66/r2/final) |
| GDPR | Security of processing, accountability, breach assessment and notification | [EUR-Lex Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| ISO/IEC 27001:2022 | ISMS incident, corrective action, audit, and management-review evidence | [ISO/IEC 27001](https://www.iso.org/standard/27001.html) |
| SOC 2 | AICPA Trust Services Criteria and independent attestation evidence | [AICPA Trust Services Criteria](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria) |
| NIS2 | Cybersecurity risk-management measures and incident reporting | [EUR-Lex NIS2 Directive](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) |

Applicability must be decided by the organization. For example, HIPAA depends
on covered-entity/business-associate status; GDPR depends on jurisdiction and
controller/processor roles; NIS2 depends on entity, sector, size, and national
transposition; ISO 27001 and SOC 2 depend on a defined scope and audit period.

## Implemented Control Catalog

| ID | Control focus | Required evidence | Typical owner |
| --- | --- | --- | --- |
| `HIPAA-164.308(a)(1)` | Risk analysis, risk treatment, sanctions, activity review | Risk analysis, treatment record, activity review, incident record | Security and Privacy Officer |
| `HIPAA-164.308(a)(6)` | Incident response and outcome documentation | Incident ticket, timeline, containment record, outcome record | Incident Response Lead |
| `HIPAA-164.312(b)` | ePHI audit controls | Audit sample, source inventory, retention policy, review record | Security Operations |
| `HIPAA-164.316` | Policies, procedures, retention, updates | Policy, procedure, review, retention records | Compliance and Security Officer |
| `NIST-CSF-2.0-RS.MA` | Coordinated response management | Ticket, triage, response, lessons learned | Incident Response Lead |
| `NIST-SP-800-61r3` | Incident response lifecycle | Plan, ticket, timeline, after-action report | Incident Response Lead |
| `GDPR-ART32` | Risk-appropriate security measures | Risk assessment, technical measures, organisational measures, effectiveness test | Data Protection Officer |
| `GDPR-ART33` | Personal-data breach decision and notification | Breach assessment, notification decision, clock, notification record | Data Protection Officer |
| `NIST-SP-800-66r2` | HIPAA safeguards assessment | Risk analysis, PHI inventory, safeguards assessment, corrective-action plan | Privacy and Security Officers |
| `ISO-27001-INCIDENT` | ISMS incident and assurance evidence | ISMS scope, incident, corrective action, internal audit, management review | ISMS Manager |
| `SOC2-CC7` | Monitoring and incident response controls | Control description, alert population, samples, approvals, auditor testing | Control Owner and SOC 2 Auditor |
| `NIS2-ART21-23` | Risk management and reporting clocks | Scope decision, policy, classification, early warning, notification, final report | Legal, Risk, and Incident Response |

## Evidence Quality Factors

The assessor evaluates more than whether a string exists:

- **Applicability**: framework, jurisdiction, entity type, service, and scope.
- **Coverage**: all required evidence fields for the control.
- **Provenance**: source system such as SIEM, EDR, IAM, ITSM, GRC, or DLP.
- **Timestamp**: collection, decision, execution, review, and notification times.
- **Integrity**: hash, immutable object ID, WORM reference, or chain-of-custody record.
- **Accountability**: control owner, approver, ticket, and execution identity.
- **Freshness**: last review and retention period relative to the control.
- **Auditability**: population, sampling method, period, and auditor reference.
- **Impact**: PHI/data categories, affected records, assets, service disruption, and severity.
- **Reporting clocks**: HIPAA, GDPR, or NIS2 deadlines and decision timestamps.
- **Human review**: control owner, privacy/legal reviewer, management, or independent auditor.

## Integration Input

Pass applicability and evidence into the orchestrator state:

```python
{
    "compliance_context": {
        "hipaa_applicable": True,
        "gdpr_applicable": False,
        "iso_scope": True,
        "soc2_scope": True,
        "nis2_applicable": False,
    },
    "compliance_evidence": {
        "HIPAA-164.308(a)(6)": {
            "incident_ticket": "INC-2026-0001",
            "timeline": "siem://cases/INC-2026-0001/timeline",
            "containment_record": "edr://actions/abc123",
            "outcome_record": "itsm://changes/CHG-1001",
            "ticket_id": "INC-2026-0001",
            "approver": "soc-manager@example.org",
            "execution_time": "2026-08-20T12:00:00Z",
            "source_system": "siem",
            "integrity_hash": "sha256:...",
        }
    },
}
```

A future production connector should populate these records from actual APIs,
not from generated text. Recommended connectors include the SIEM case system,
EDR action history, IAM audit logs, ITSM/change management, GRC control library,
DLP/PHI classification, backup/DR testing, and notification-management systems.
