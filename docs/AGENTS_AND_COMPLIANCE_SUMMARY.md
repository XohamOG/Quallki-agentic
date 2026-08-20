# QUAL-KI SOC Agents and Compliance Summary

## 1. Purpose

QUAL-KI is a healthcare-focused Security Information and Event Management (SIEM)
prototype. It receives telemetry and logs, detects suspicious activity, assesses
risk, routes the incident through specialist agents, and produces an auditable
incident and compliance-evidence record.

The system is designed for defensive operations. Its built-in healthcare cases
are synthetic simulations. Response actions are recommendations unless a future,
approved integration executes them in a real security system.

## 2. Complete Agent Flow

```text
Telemetry, logs, feature vector, and asset context
                    |
                    v
            Detection Agent
                    |
                    v
             Triage Agent
                    |
          +---------+---------+
          |                   |
   Investigation path    Response path
          |                   |
          +---------+---------+
                    |
                    v
          Threat Intelligence Agent
                    |
                    v
             Response Agent
                    |
                    v
             Forensics Agent
                    |
                    v
            Compliance Agent
                    |
                    v
             Finalize Summary
```

If triage classifies an event as low risk, the workflow can route to an
`auto_close` path. The current healthcare scenarios normally use investigation
or response paths.

## 3. Agent Roles

### 3.1 Telemetry Ingestion

**Module:** `src/quallki_agentic/telemetry/`

Receives or simulates security events and creates a normalized input containing:

- Alert message
- Source IP
- Event time
- Telemetry source
- Time window
- Network-flow features
- Host security features
- Raw logs

In production, this layer should connect to real sources such as Wazuh, Sysmon,
EDR, firewall, IDS/IPS, identity provider, network-flow collector, cloud audit
logs, and clinical application audit logs.

### 3.2 Detection Agent

**Module:** `src/quallki_agentic/agents/detection_agent.py`

The Detection Agent creates the structured alert object.

It performs:

1. QML inference using the supplied autoencoder and VQC.
2. 99-feature validation and construction.
3. Learned reduction from 99 features to 6 latent values.
4. Six-qubit VQC classification.
5. Log and IOC extraction.
6. Attack-vector identification.
7. Likely CWE identification.
8. CWSS-like severity scoring.
9. Composite confidence calculation.
10. Affected-asset identification.

The active model flow is:

```text
99 features
  -> Linear(99,64)
  -> ReLU
  -> Linear(64,6) autoencoder encoder
  -> 6-qubit AngleEmbedding/VQC
  -> Linear(6,10)
  -> attack label
```

The Detection Agent returns an `alert_object` containing:

- `qml_label`
- `qml_backend`
- `composite_confidence`
- `analysis.attack_vector`
- `analysis.evidence`
- `analysis.iocs`
- `analysis.likely_cwes`
- `analysis.affected`
- `cwss.score`
- Original event and asset metadata

The model label does not provide confidence. Confidence is calculated from
observable evidence, IOCs, severity, label signal, and telemetry signal strength.

### 3.3 Triage Agent

**Module:** `src/quallki_agentic/agents/triage_agent.py`

The Triage Agent decides how urgently the event should be handled.

It considers:

- Composite confidence
- CWSS-like score
- Clinical impact
- Attack vector
- Affected assets
- Detected label

It produces:

- Priority: `P0`, `P1`, or `P2`
- Route: response or investigation
- Reasoning
- Impact classification
- Affected assets
- Recommended fixes
- Auto-close decision

Healthcare systems require clinical safety awareness. For example, isolating an
EHR, PACS, or infusion-pump management system may require coordination with
clinical operations before disruptive action.

### 3.4 Threat Intelligence Agent

**Module:** `src/quallki_agentic/agents/threat_intel_agent.py`

Enriches the alert with external and internal threat context.

Current responsibilities:

- Classify IP indicators as network-discovery context.
- Convert CVE identifiers into NVD links.
- Add ATT&CK technique identifiers.
- Associate possible campaigns or intrusion context.

Production extensions should connect to approved threat-intelligence sources,
asset reputation services, vulnerability scanners, ISAC feeds, NVD/CVE data,
and internal threat reports.

### 3.5 Response Agent

**Module:** `src/quallki_agentic/agents/response_agent.py`

Creates proposed containment and mitigation actions.

Examples:

- Block a malicious source IP.
- Revoke active credentials or tokens.
- Isolate an affected endpoint.
- Notify clinical operations before service restart.
- Start PHI impact assessment.
- Preserve legal and audit evidence.

The current implementation only returns recommendations. It does not call a
firewall, EDR, IAM, ticketing, or hospital system.

A production response integration must include:

- Strong authentication
- Role-based authorization
- Human approval for disruptive actions
- Clinical safety gates
- Idempotency
- Rollback procedures
- Complete execution logging
- Evidence of the actual action result

### 3.6 Forensics Agent

**Module:** `src/quallki_agentic/agents/forensics_agent.py`

Builds an incident timeline summary from:

- Alert event time
- Raw logs
- IOCs
- Detection evidence
- Triage priority
- Threat-intelligence context
- Response actions

Production forensics should preserve original logs, hashes, collection times,
chain of custody, analyst actions, and evidence storage references.

### 3.7 Compliance Agent

**Module:** `src/quallki_agentic/agents/compliance_agent.py`

The Compliance Agent is an evidence assessor for the SIEM. It does not make a
legal, regulatory, certification, or attestation decision.

It evaluates whether declared evidence exists for applicable controls and returns:

- Control applicability
- Evidence status
- Evidence present
- Evidence missing
- Evidence source system
- Last evidence time
- Quality factors
- Control owner
- Official source URL
- Human-review requirement
- Assessment metrics

### 3.8 Finalize Node

**Module:** `src/quallki_agentic/orchestrator/nodes.py`

Combines the outputs from all agents into a final SOC incident summary
containing:

- Priority
- Triage reasoning
- ATT&CK context
- Containment recommendations
- Forensics summary
- Compliance evidence posture

## 4. Compliance Assessment Model

The checklist is an evidence mapping, not a compliance certificate.

The system deliberately does not return:

```text
compliant
certified
attested
done
```

Instead, it returns these evidence statuses:

| Status | Meaning |
| --- | --- |
| `not_applicable` | The supplied applicability context says the control does not apply. |
| `not_evidenced` | The control applies, but no required evidence was supplied. |
| `partial` | Some required evidence exists, but required fields are missing. |
| `evidence_complete` | All declared evidence fields exist and are ready for human review. |

Even `evidence_complete` does not mean the organization is compliant.

## 5. Compliance Sources

The implementation maps controls to these official sources.

| Framework/source | What it supports | Official source |
| --- | --- | --- |
| HIPAA Security Rule | Administrative, physical, and technical safeguards; incident procedures; audit controls; documentation | [eCFR Title 45 Part 164 Subpart C](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C) |
| HHS HIPAA Breach Notification Rule | PHI breach risk assessment, notification, and documentation | [HHS Breach Notification Rule](https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html) |
| NIST CSF 2.0 | Cybersecurity risk outcomes and response mapping | [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) |
| NIST SP 800-61 Rev. 3 | Incident response lifecycle and operational recommendations | [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) |
| NIST SP 800-66 Rev. 2 | HIPAA Security Rule implementation guidance | [NIST SP 800-66 Rev. 2](https://csrc.nist.gov/pubs/sp/800/66/r2/final) |
| GDPR | Security of processing, accountability, breach assessment, and notification | [EUR-Lex GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| ISO/IEC 27001:2022 | ISMS scope, incidents, corrective actions, audits, and management review | [ISO/IEC 27001](https://www.iso.org/standard/27001.html) |
| SOC 2 | AICPA Trust Services Criteria and independent attestation evidence | [AICPA Trust Services Criteria](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria) |
| NIS2 Directive | Cybersecurity risk-management measures and incident reporting | [EUR-Lex NIS2 Directive](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) |

Applicability must be decided by the organization. HIPAA, GDPR, ISO 27001, SOC
2, and NIS2 do not automatically apply to every healthcare application.

## 6. Compliance Factors Considered

### 6.1 Applicability

The SIEM must know whether a control applies based on:

- Covered-entity or business-associate status
- Processing of ePHI or other health data
- GDPR jurisdiction and controller/processor role
- ISO 27001 ISMS scope
- SOC 2 service and trust-services scope
- NIS2 entity type, sector, size, and jurisdiction
- National law and sector-specific rules

### 6.2 Evidence Coverage

Each control defines required evidence fields. Examples include:

- Incident ticket
- Incident timeline
- Risk analysis
- Risk treatment
- Audit-log sample
- Log-source inventory
- Retention policy
- IAM review
- Containment execution record
- PHI inventory
- Breach assessment
- Notification decision
- Early warning
- Incident notification
- Final report
- Internal audit
- Management review
- Independent auditor testing

### 6.3 Provenance

Evidence must identify where it came from:

- SIEM
- EDR
- IAM
- Firewall
- DLP
- ITSM
- GRC platform
- Backup/DR platform
- Clinical application audit log
- Privacy or legal workflow

Generated text is not equivalent to authoritative system evidence.

### 6.4 Time and Freshness

The assessment considers:

- Event time
- Evidence collection time
- Decision time
- Approval time
- Execution time
- Notification time
- Last control review
- Retention period
- Reporting deadlines

### 6.5 Integrity and Chain of Custody

Production evidence should include:

- SHA-256 or equivalent hash
- Immutable object ID
- WORM or retention-lock reference
- Original source identifier
- Collector identity
- Collection timestamp
- Chain-of-custody record

### 6.6 Accountability

Evidence should identify:

- Control owner
- Incident owner
- Approver
- Executing identity
- Privacy or legal reviewer
- Management approver
- Independent auditor, where required

### 6.7 Incident Impact

The SIEM records impact factors including:

- PHI or personal-data involvement
- Data categories
- Number of affected records
- Affected systems and assets
- Service disruption
- Clinical impact
- Confidentiality, integrity, and availability impact
- Cross-border impact
- Financial or operational impact
- Likelihood of harm
- Mitigation already performed

### 6.8 Reporting Deadlines

The system can track reporting decisions and timestamps, but it must not make
legal decisions automatically.

Examples:

- HIPAA breach notification assessment and documentation
- GDPR supervisory-authority notification decision and 72-hour clock
- NIS2 early warning within 24 hours
- NIS2 incident notification within 72 hours
- NIS2 final report within one month

The responsible privacy, legal, security, or regulatory owner must make the final
determination.

## 7. SIEM Evidence Input

Real integrations should provide this structure to the orchestrator:

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

The orchestrator preserves both `compliance_context` and
`compliance_evidence` through the agent graph.

## 8. What This SIEM Can and Cannot Claim

### It can claim

- A control is applicable according to supplied context.
- A required evidence field is present or missing.
- Evidence came from a declared source system.
- A timeline or notification clock is recorded.
- An incident event was observed by the SIEM.
- A control evidence package is complete for human review.
- Gaps and remediation requirements exist.

### It cannot claim by itself

- HIPAA compliance
- GDPR compliance
- ISO 27001 certification
- SOC 2 attestation
- NIS2 compliance
- Legal breach notification decisions
- Auditor approval
- Correctness of an external system record
- That a recommended response action was actually executed

Those claims require organizational governance, approved policies, authoritative
records, qualified reviewers, and independent audit or regulatory processes where
applicable.

## 9. Production Integration Roadmap

To make this a production SIEM compliance capability, connect:

1. SIEM case management for incident IDs, timelines, and analyst actions.
2. EDR for isolation and remediation execution records.
3. IAM for access reviews, token revocation, MFA, and privileged activity.
4. Network controls for firewall, IDS, IPS, and flow evidence.
5. ITSM/change management for approved changes and outcomes.
6. GRC platform for control ownership, policies, risk registers, and exceptions.
7. DLP and data inventory for PHI and personal-data classification.
8. Backup/DR platforms for recovery-test evidence.
9. Privacy/legal systems for breach qualification and notification decisions.
10. Immutable evidence storage with access control and chain of custody.
11. Auditor workflows for sampling, review, exceptions, and sign-off.
12. Human approval gates for clinical or disruptive response actions.
