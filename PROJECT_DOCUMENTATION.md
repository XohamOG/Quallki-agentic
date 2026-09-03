# QUAL-KI Agentic SOC — Full Project Documentation

> A Healthcare-Focused Quantum-Classical AI Security Operations Center Prototype

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [ML Pipeline — Quantum + Classical](#3-ml-pipeline--quantum--classical)
4. [Dataset & Feature Engineering](#4-dataset--feature-engineering)
5. [Agentic Workflow](#5-agentic-workflow)
6. [Agent Descriptions](#6-agent-descriptions)
7. [Compliance Evidence System](#7-compliance-evidence-system)
8. [Streamlit Dashboard](#8-streamlit-dashboard)
9. [Demo Log Files](#9-demo-log-files)
10. [Running the Application](#10-running-the-application)
11. [Configuration Reference](#11-configuration-reference)
12. [Key Findings & Limitations](#12-key-findings--limitations)

---

## 1. Project Overview

**QUAL-KI** (Quantum-AI Security Operations Intelligence) is a healthcare-focused **Agentic SOC** prototype that demonstrates the future of Tier-1/Tier-2 autonomous SOC operations. It leverages:

- A streamlined **7-Agent LangGraph Framework** capable of automating routine alert triage (the 70% threshold) using cognitive reasoning.
- **Dual-LLM Orchestration** — NVIDIA Nemotron-3-Ultra-550b prioritized for primary inference, with a seamless, zero-downtime fallback to Google Gemini-3.5-Flash.
- **Structured Pydantic Outputs** (`.with_structured_output()`) to guarantee deterministic routing and data extraction (e.g., `TriageVerdict`) without parsing ambiguity.
- **Quantum Machine Learning (QML)** — a 6-qubit Variational Quantum Circuit (VQC) running alongside a classical LightGBM model for threat detection.
- A **deterministic CWSS v1.0.1 scoring engine** embedded directly into the Threat Intel Agent to bridge MITRE ATT&CK techniques with CAPEC and CWE vulnerabilities.
- A **compliance evidence mapping** system assessing posture across HIPAA, NIST, ISO 27001, GDPR, and more.

The system accepts real SIEM-style JSON logs and routes them through the LangGraph pipeline, producing actionable containment recommendations, blast-radius hypotheses, and a regulatory compliance posture report—all viewable on a real-time Streamlit dashboard.

> **Important:** This is a research prototype. It does not send packets, execute attacks, contact real hospital systems, or make automated changes to infrastructure.

---

## 2. Architecture

```
              Input Sources
         log1.json – log6.json (real dataset rows)
         sample_alerts/*.json  (sanitized fixtures)
         Streamlit Upload / CLI --input
                   |
                   v
          ┌────────────────────┐
          │   Detection Agent   │
          │  99-Feature Vector  │
          │  QML VQC Pipeline   │──> qml_label
          │  Classical LightGBM │──> classical_label
          │  Log Analyzer       │──> IOCs, CWEs, evidence
          │  CWSS Scorer        │──> cwss_score
          │  Confidence Agg.    │──> composite_confidence
          └────────┬───────────┘
                   |
         ┌─────────v──────────────────────────────────┐
         │             LangGraph Pipeline              │
         │                                             │
         │  Triage ──> Threat Intel ──> Response       │
         │      |                                      │
         │  Forensics ──> Compliance ──> Finalize      │
         └─────────────────────────────────────────────┘
                   |
          ┌────────v───────────┐
          │  Streamlit Dashboard│
          │  10 tabs of output  │
          └─────────────────────┘
```

---

## 3. ML Pipeline — Quantum + Classical

### 3.1 Quantum ML VQC Pipeline

#### Stage 1: Preprocessing (qml_preprocessing.json)
```
99 raw features
    |
log1p transform on 19 heavy-tailed features
(flow_byts_s, totlen_fwd_pkts, fwd_blk_rate_avg, etc.)
    |
StandardScaler (training-only statistics, 149,196 rows)
```

#### Stage 2: Autoencoder (best_qml_autoencoder_6q.pt)
```
99 scaled features
    |  Linear(99, 64) -> ReLU -> Linear(64, 6)
    v
6-dimensional latent vector
    |
Scale to [-pi, pi] using training latent min/max
```

#### Stage 3: Variational Quantum Circuit (best_qml_vqc_6q.pt)
```
6 angle-embedded values
    |
AngleEmbedding (6 qubits, rotation Y)
    |
StronglyEntanglingLayers (4 layers x 6 qubits x 3 params)
    |
6x PauliZ measurements
    |
Linear(6, 10) -> 10-class prediction -> Attack Label
```

#### 10 Attack Classes

| Index | Dataset Label | Canonical Name |
|-------|--------------|----------------|
| 0 | BaseLine | normal |
| 1 | Alice2 | alice2 |
| 2 | DevEva | deveva |
| 3 | Discov | recon |
| 4 | Hulk | dos |
| 5 | Nmap | recon |
| 6 | NosyN | nosyn |
| 7 | Ransac | ransomware |
| 8 | SlowLoris | dos |
| 9 | SuperSpy | superspy |

> **Known Limitation:** The 6-qubit VQC has limited expressivity and currently exhibits a dominant-class bias toward `ransomware`. This is a known challenge with low-qubit quantum classifiers. Treat the VQC output as a research-grade signal — not a production classifier.

---

### 3.2 Classical LightGBM Model

The classical model (`best_regularized_model.joblib`) is a trained LightGBM gradient boosting classifier:

- **Input:** Same 99-feature vector as QML
- **Output:** One of the 10 attack class labels
- **Reliability:** Significantly higher accuracy across all attack classes vs. the QML VQC
- **Role in Pipeline:** Runs alongside QML — both predictions shown side-by-side in the Model Comparison tab

#### Verified predictions on real dataset rows

| True Attack Type | Classical | QML |
|------------------|-----------|-----|
| BaseLine | normal (correct) | ransomware |
| SlowLoris | dos (correct) | ransomware |
| Nmap | recon (correct) | ransomware |
| Ransac | ransomware (correct) | ransomware (correct) |

---

### 3.3 Generating the QML Preprocessing Artifact

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe scripts\fit_qml_preprocessing.py `
  --csv MasterDatasetProcessed_Clean.csv `
  --log-features flow_duration,flow_byts_s,flow_pkts_s,totlen_fwd_pkts,flow_iat_mean,...
```

Generated from 149,196 training rows. Output: `qml_preprocessing.json` (StandardScaler stats + latent bounds).

---

## 4. Dataset & Feature Engineering

### 4.1 Dataset

**File:** `MasterDatasetProcessed_Clean.csv`
**Size:** ~84 MB, 149,196+ rows

### 4.2 Data Sources Combined

| Source | Features |
|--------|----------|
| CICFlowMeter | Network flow metrics (packets, bytes, IAT, flags) |
| Wazuh | OS event volume, severity, high-severity count |
| Sysmon | Process event count |
| PAM/sudo | Privilege escalation events |
| Port encoding | dst_port_443, dst_port_22, dst_port_80, etc. (one-hot) |
| Protocol encoding | proto_tcp, proto_udp, proto_other |

### 4.3 19 Heavy-Tailed Features (log1p Transformed)

These features had skewness > 19 and were log-transformed before scaling:

```
bwd_byts_b_avg, totlen_bwd_pkts, subflow_bwd_byts, subflow_fwd_byts,
totlen_fwd_pkts, fwd_blk_rate_avg, bwd_blk_rate_avg, bwd_psh_flags,
fwd_byts_b_avg, flow_byts_s, fwd_seg_size_avg, fwd_pkt_len_mean,
fwd_act_data_pkts, pkt_len_var, fwd_psh_flags, fwd_header_len,
bwd_pkts_b_avg, tot_fwd_pkts, subflow_fwd_pkts
```

---

## 5. Agentic Workflow

The system is built on **LangGraph** — a stateful, directed graph of 7 agent nodes. It utilizes an **OrchestratorState** shared memory dictionary, allowing agents to sequentially read and write context.

```
Input Alert JSON
       |
       v
 Detection Node  --> alert_object, qml_label, classical_label, cwss, iocs
       |
       v
 Triage Node     --> TriageVerdict (Pydantic: priority, threat_hypothesis, blast_radius, auto_close_rationale)
       |
       +-------------------+ (If AUTO_CLOSE_FALSE_POSITIVE) ---> Finalize
       | (If ESCALATE_HIGH or CONTAIN_CRITICAL)
       v
 Threat Intel   --> ATT&CK techniques, Deterministic CWSS Score, CWE Mapping
       |
       v
 Response Node  --> containment actions (LLM-generated based on Threat Intel)
       |
       v
 Forensics Node --> incident timeline (LLM-generated narrative)
       |
       v
 Compliance Node --> evidence posture for 12 controls
       |
       v
 Finalize Node  --> final SOC summary string
```

---

## 6. Agent Descriptions

### 6.1 Multi-LLM Fallback Engine
All cognitive agents (Triage, Threat Intel, etc.) utilize a highly resilient `llm_helper.py` backend. The engine attempts to initialize `ChatNVIDIA(model="nvidia/nemotron-3-ultra-550b-a55b")`. If the NVIDIA API key is missing or the NIM endpoint returns a 503 Overloaded error, the system safely catches the exception and falls back to `ChatGoogleGenerativeAI(model="gemini-3.5-flash")` with zero downtime.

### 6.2 Detection Agent
1. Parses `message`, `source_ip`, `asset_type` from raw logs.
2. Runs QML VQC -> `qml_label`
3. Runs Classical LightGBM -> `classical_label`
4. Log Analyzer: Extracts IOCs, attack vectors.

### 6.3 Triage Agent
The Triage Agent operates as an autonomous Tier-1/Tier-2 analyst. It uses `.with_structured_output(TriageVerdict)` to return a rigid Pydantic model. It performs multi-modal deduplication, assesses asset blast radius, auto-closes benign telemetry with defensible audit logs (handling the 70% automation threshold), and formulates the initial threat hypothesis that drives targeted specialist agent activation.

### 6.4 Threat Intel Agent
- Maps IOCs and triage context to MITRE ATT&CK techniques.
- Embeds a **Deterministic CWSS v1.0.1 scoring engine**, calculating a Base, Target, and Environmental score.
- Establishes a local crosswalk dictionary to bridge ATT&CK behaviors with CWE software flaws.

### 6.5 Response & Forensics Agents
- **Response Agent:** Generates 3-5 specific, actionable containment steps based on the Threat Hypothesis.
- **Forensics Agent:** Reconstructs a timeline narrative based on raw logs and triage priority.

### 6.6 Compliance Agent
- Runs `assess_compliance()` to evaluate 12 regulatory controls.
- Returns checklist, metrics, and a detailed, evidence-linked compliance explanation.

---

## 7. Compliance Evidence System

### 7.1 Control Catalog (12 Controls)

| Control ID | Framework | Applicability |
|-----------|-----------|---------------|
| HIPAA-164.308(a)(1) | HIPAA Security Rule | hipaa_applicable |
| HIPAA-164.308(a)(6) | HIPAA Security Rule | hipaa_applicable |
| HIPAA-164.312(b) | HIPAA Security Rule | hipaa_applicable |
| HIPAA-164.316 | HIPAA Security Rule | hipaa_applicable |
| NIST-CSF-2.0-RS.MA | NIST CSF 2.0 | always |
| NIST-SP-800-61r3 | NIST SP 800-61 Rev. 3 | always |
| GDPR-ART32 | GDPR Article 32 | gdpr_applicable |
| GDPR-ART33 | GDPR Article 33 | gdpr_applicable |
| NIST-SP-800-66r2 | NIST SP 800-66 Rev. 2 | hipaa_applicable |
| ISO-27001-INCIDENT | ISO/IEC 27001:2022 | iso_scope |
| SOC2-CC7 | AICPA SOC 2 | soc2_scope |
| NIS2-ART21-23 | EU NIS2 Directive | nis2_applicable |

### 7.2 Evidence Status Values

| Status | Meaning |
|--------|---------|
| evidence_complete | All required evidence fields supplied |
| partial | Some fields present, some missing |
| not_evidenced | Control applicable but no evidence provided |
| not_applicable | Control not applicable per compliance_context |

### 7.3 How to Provide Evidence

```json
{
  "compliance_context": {
    "hipaa_applicable": true,
    "iso_scope": true,
    "gdpr_applicable": false
  },
  "compliance_evidence": {
    "HIPAA-164.308(a)(6)": {
      "incident_ticket": "INC-2026-1099",
      "timeline": "Attack occurred 01:00:00 - 01:02:30 UTC",
      "containment_record": "Host isolated at 01:02:30 UTC",
      "outcome_record": "Portal restored at 01:04:00 UTC",
      "approver": "SOC Lead",
      "integrity_hash": "sha256:..."
    }
  }
}
```

---

## 8. Streamlit Dashboard

**URL:** `http://localhost:8502`

### Tab Guide

| Tab | Content |
|-----|---------|
| Overview | Alert metadata, logs, detection evidence, IOCs, CWSS score |
| Detection | Full alert_object JSON from Detection Agent |
| Model Comparison | QML vs Classical label, architecture notes, trust guidance |
| Triage | Priority (P0/P1/P2), confidence, Gemini reasoning, fixes |
| Threat Intel | ATT&CK techniques, CVE links, related campaigns |
| Response | Gemini-generated containment actions |
| Forensics | Gemini-generated attack timeline narrative |
| Compliance | Coloured control cards + clickable source links + raw table |
| LangGraph Trace | Per-node state updates from the actual graph run |
| SOC Summary | Final executive incident summary string |

---

## 9. Demo Log Files

| File | Scenario | Attack Type | Notes |
|------|----------|-------------|-------|
| log1.json | Normal backup traffic | BaseLine | Basic pipeline test |
| log2.json | Data exfiltration | Alice2 | |
| log3.json | Port scan / recon | Nmap | |
| log4.json | Ransomware on EHR server | Ransac | |
| log5.json | Ransomware + full compliance | Ransac | Shows all 4 compliance statuses |
| log6.json | Slow HTTP DoS on web portal | SlowLoris | Classical=dos, QML=ransomware (disagreement demo) |

### log5.json — Compliance Status Demo

| Control | Status |
|---------|--------|
| HIPAA-164.308(a)(6) | evidence_complete |
| HIPAA-164.308(a)(1) | partial |
| HIPAA-164.312(b) | not_evidenced |
| GDPR-ART32 | not_applicable |
| ISO-27001-INCIDENT | evidence_complete |

---

## 10. Running the Application

### Install

```powershell
cd d:\Quallki-agentic
.\.venv\Scripts\python.exe -m pip install -e .
```

### Start Streamlit

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\streamlit.exe run src/quallki_agentic/ui/streamlit_app.py --server.port 8502
```

### CLI Commands

```powershell
$env:PYTHONPATH = "src"

# Real log file
.\.venv\Scripts\python.exe -m quallki_agentic.cli --input log5.json

# Synthetic scenario
.\.venv\Scripts\python.exe -m quallki_agentic.cli --scenario ehr_ransomware
```

---

## 11. Configuration Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| NVIDIA_API_KEY | — | Authenticates NVIDIA Nemotron-3-Ultra |
| GEMINI_API_KEY | — | Authenticates Gemini LLM (Fallback) |
| GEMINI_MODEL | gemini-3.5-flash | Fallback LLM model |
| USE_GEMINI | true | Enables Gemini fallback |
| QML_MODEL_PATH | best_qml_vqc_6q.pt | 6-qubit VQC checkpoint |
| QML_AUTOENCODER_PATH | best_qml_autoencoder_6q.pt | Autoencoder checkpoint |
| QML_PREPROCESSING_PATH | qml_preprocessing.json | Scaler + latent bounds |
| DEMO_MODE | true | Enables synthetic scenarios |

---

## 12. Key Findings & Limitations

### What Works

- **Real log ingestion:** upload any JSON with logs + features -> full 7-agent pipeline runs.
- **QML inference:** 6-qubit VQC loaded via PennyLane + PyTorch, runs quantum circuit inference.
- **Classical inference:** LightGBM correctly classifies all 10 attack types.
- **Dual-LLM Engine:** Resilient failover from NVIDIA Nemotron 550b to Gemini 3.5 Flash successfully bypasses `503 Overloaded` API errors with zero downtime.
- **Pydantic Extraction:** `.with_structured_output()` ensures deterministic parsing of LLM logic across all cognitive agents.
- **Compliance mapping:** 12 controls assessed per upload, clickable regulatory links in UI.

### Known Limitations

| Issue | Root Cause | Impact |
|-------|-----------|--------|
| QML always predicts ransomware | 6-qubit VQC dominant-class collapse | Disagreement on all non-Ransac logs |
| Threat Intel relies on LLM Knowledge | ATT&CK to CWE mapping uses a local dictionary | Emerging threats may need manual updates to the dictionary |
| Keyword-based log analysis | Deterministic heuristics, not a SIEM | Evidence quality depends on log verbosity |
| CWSS is a heuristic | Calculated via custom script, not a vulnerability scanner | Useful for relative ranking only |
| Compliance is not legal advice | AI cannot certify compliance | Requires human validation |

### Potential Next Steps

1. Retrain QML with more qubits (12-16) or better class-balancing.
2. Add real SIEM adapter (Wazuh API, Splunk, Elastic).
3. Connect the Threat Intel agent directly to MITRE/CVE APIs instead of offline dictionaries.
4. Add analyst feedback capture and incident history.
5. Add approval gates for clinical response actions
6. Add PHI minimization and audit logging for production

---

*Documentation generated: 2026-08-21 | QUAL-KI Agentic SOC v0.1 (Research Prototype)*
