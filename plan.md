# Plan: QML-stub detection + confidence aggregator + CWSS + log analysis
This plan implements the workflow you described: the QML model (stubbed for now) returns only an attack category; the detection pipeline computes a composite confidence score from multiple signals, analyzes logs/telemetry to infer attack vector/evidence/likely CWEs, scores weaknesses with a CWSS-like heuristic, and then triage produces priority, affected systems, impact, and remediation guidance.

Paste this file into Copilot (or a coding agent) and run it. It is intentionally prescriptive: which files to create/modify, expected behavior, tests, and acceptance criteria.

---

## High-level flow to implement
1. QML stub: returns only `label` (attack category). No confidence value returned by the model.
2. DetectionAgent:
   - Calls QML stub to obtain `qml_label`.
   - Runs a log analyzer to extract evidence, attack_vector, IOCs, and likely CWE candidates.
   - Runs CWSS-like scoring to produce a numeric severity score (0..10).
   - Aggregates a composite confidence score computed from: presence of IOCs, evidence, CWSS score, label-based heuristics, and optional telemetry signals.
   - Returns an enriched `alert_object` containing `composite_confidence`, `analysis` (attack_vector, evidence, likely_cwes, affected), and `cwss`.
3. TriageAgent:
   - Uses `composite_confidence`, `cwss.score`, `attack_vector`, and `clinical_impact` to set priority (P0/P1/P2), reasoning, recommended fixes, and affected assets.
4. No classical fallback model is used anywhere; references to classical fallback must be removed or disabled — keep a QML stub only.
5. Keep changes localized so CI / other flows are minimally affected.

---

## Files to add
Create these three helper modules:

1. `src/quallki_agentic/qml_stub.py` (QML stub)
```python
# src/quallki_agentic/qml_stub.py
from __future__ import annotations
from typing import Dict, Any
import os

def infer(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    QML stub: returns only a label (attack category). No confidence.
    If QML_ENDPOINT_URL is set, this function is a placeholder for calling it.
    For now, it echoes back payload["qml_label"] or attempts a heuristic.
    """
    qml_label = payload.get("qml_label")
    if qml_label:
        return {"label": str(qml_label)}
    # simple heuristic fallback for demo:
    msg = str(payload.get("message", "")).lower()
    if "ransom" in msg or "encrypt" in msg:
        return {"label": "ransomware"}
    if "sql" in msg or "select " in msg:
        return {"label": "sql-injection"}
    if "credential" in msg or "login failed" in msg:
        return {"label": "credential-theft"}
    return {"label": "unknown"}