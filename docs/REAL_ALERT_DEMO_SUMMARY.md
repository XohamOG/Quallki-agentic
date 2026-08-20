# QUAL-KI Real Alert Demo Summary

## Purpose

This document explains how to run sanitized alert fixtures through the QUAL-KI
SIEM workflow using the updated dataset feature contract.

The fixtures are realistic test inputs, not captured production logs. They use
RFC 5737 documentation IP ranges and do not contact or modify real systems.

## Dataset Feature Pipeline

The model training pipeline produces 99 features from:

- CICFlowMeter network-flow metrics
- Wazuh host-security telemetry
- Sysmon process events
- PAM/sudo activity
- Severity counts
- Port one-hot encoding
- Protocol one-hot encoding

The documented QML preprocessing flow is:

```text
99 cleaned features
    |
log1p on the exact 19 heavy-tailed training features
    |
training-only StandardScaler
    |
Autoencoder: 99 -> 64 -> 6
    |
training-only latent min/max bounds
    |
scale latent values to [-pi, pi]
    |
6-qubit VQC
    |
10-class attack label
```

Raw 99-feature inference requires `qml_preprocessing.json`. That file must be
created from training-only data using the original 19 log-transformed feature
names, training means/scales, and latent min/max values.

Without that artifact, the system reports `heuristic_stub` rather than silently
using invalid model preprocessing.

## Available Alert Fixtures

Located in `sample_alerts/`:

| File | Simulated event |
| --- | --- |
| `ehr_ransomware.json` | PowerShell execution, shadow-copy deletion, mass encryption, SMB movement |
| `pacs_recon.json` | TCP scanning, DICOM enumeration, repeated PACS connection attempts |
| `infusion_pump_credential_abuse.json` | Failed logins, token misuse, MFA challenge |
| `alerts.jsonl` | Batch containing all three alert records |

Each alert can include:

- `alert_id`
- `message`
- `event_time`
- `source_ip`
- `asset_type`
- `clinical_impact`
- `contains_phi`
- `logs`
- `features`
- `telemetry_signals`
- `compliance_context`
- `compliance_evidence`

## Complete Agent Flow

Every uploaded alert is passed through the compiled LangGraph:

```text
Input JSON/JSONL
     |
Detection Agent
     |
Triage Agent
     |
Threat Intelligence Agent
     |
Response Agent
     |
Forensics Agent
     |
Compliance Agent
     |
Finalize Node
```

### Detection Agent

- Validates and builds the 99-feature vector
- Runs QML preprocessing and classification when artifacts are available
- Extracts evidence from logs
- Extracts IOCs
- Identifies attack vector and likely CWEs
- Calculates CWSS-like severity
- Calculates composite confidence

### Triage Agent

- Uses composite confidence
- Uses CWSS-like score
- Considers clinical impact
- Identifies affected assets
- Assigns P0, P1, or P2
- Selects response or investigation routing
- Produces recommended fixes

### Threat Intelligence Agent

- Maps IP indicators to network-discovery context
- Converts CVE indicators to NVD links
- Adds ATT&CK technique context

### Response Agent

Produces proposed actions such as:

- Source blocking
- Token revocation
- Endpoint isolation
- Clinical operations notification
- PHI impact assessment
- Evidence preservation

These are recommendations only unless approved integrations are connected.

### Forensics Agent

Produces an incident timeline summary from the alert, logs, IOCs, triage, and
response context.

### Compliance Agent

Assesses control evidence against the configured applicability context.
Possible statuses are:

- `not_applicable`
- `not_evidenced`
- `partial`
- `evidence_complete`

The system never declares legal compliance, certification, or attestation.

## CLI Usage

Run one fixture:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m quallki_agentic.cli --input sample_alerts\ehr_ransomware.json
```

Run the JSONL batch:

```powershell
.\.venv\Scripts\python.exe -m quallki_agentic.cli --input sample_alerts\alerts.jsonl
```

The CLI displays:

- QML backend
- LangGraph nodes executed
- Detection evidence
- IOCs and CWEs
- CWSS-like score
- Triage priority
- Response actions
- Compliance evidence posture
- Final SOC summary

## Streamlit Usage

Start the dashboard:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m streamlit run src/quallki_agentic/ui/streamlit_app.py --server.port 8502
```

Open:

```text
http://localhost:8502
```

Select **Live JSON/JSONL**, upload one JSON fixture, and click **Run Agentic
SOC**.

The dashboard includes tabs for:

- Overview
- Detection
- Triage
- Threat Intel
- Response
- Forensics
- Compliance
- LangGraph Trace
- SOC Summary

The LangGraph Trace tab displays the actual state update returned by each graph
node for the uploaded alert.

## Production Integration Requirements

To replace the sanitized fixtures with production data, connect the live input
boundary to approved systems such as:

- Wazuh
- Sysmon or EDR
- Firewall and IDS/IPS
- Network-flow collector
- IAM and MFA provider
- Clinical application audit logs
- SIEM case management
- ITSM/change management
- GRC platform
- DLP and PHI classification
- Immutable evidence storage

Production integrations must add authentication, authorization, rate limiting,
PHI minimization, audit logging, evidence integrity, retention enforcement, and
human approval gates for disruptive clinical actions.

## Important Limitation

The sample fixtures exercise the full agent workflow, but they do not prove
production detection accuracy. For accurate QML inference, generate and version
`qml_preprocessing.json` from the original training-only dataset preprocessing
pipeline before using raw 99-feature production records.
