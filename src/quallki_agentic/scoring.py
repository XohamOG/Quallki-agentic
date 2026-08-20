from __future__ import annotations

from typing import Any


def score_cwss(
    label: str,
    analysis: dict[str, Any],
    clinical_impact: str,
) -> dict[str, Any]:
    label_score = {
        "ransomware": 9.0,
        "malware": 8.5,
        "sql-injection": 8.0,
        "credential-theft": 7.5,
        "brute_force": 6.5,
        "dos": 7.0,
        "recon": 4.0,
        "unknown": 2.0,
    }.get(label.lower(), 3.0)
    impact_score = {"critical": 2.0, "high": 1.5, "medium": 0.8, "low": 0.2}.get(
        clinical_impact.lower(), 0.5
    )
    evidence_score = min(1.0, len(analysis.get("evidence", [])) / 4)
    ioc_score = min(1.0, len(analysis.get("iocs", [])) / 3)
    score = min(10.0, round(label_score * 0.65 + impact_score + evidence_score + ioc_score, 2))
    return {
        "score": score,
        "vector": analysis.get("attack_vector", "unknown"),
        "rationale": f"Label severity {label_score:.1f}, clinical impact {clinical_impact}, and observed evidence were combined.",
    }


def aggregate_confidence(
    label: str,
    analysis: dict[str, Any],
    cwss: dict[str, Any],
    telemetry: Any = None,
) -> float:
    label_signal = 0.9 if label.lower() != "unknown" else 0.2
    ioc_signal = min(1.0, len(analysis.get("iocs", [])) / 2)
    evidence_signal = min(1.0, len(analysis.get("evidence", [])) / 3)
    telemetry_signal = 0.0
    if isinstance(telemetry, dict):
        telemetry_signal = min(1.0, max(0.0, float(telemetry.get("signal_strength", 0.0))))
    elif isinstance(telemetry, (int, float)):
        telemetry_signal = min(1.0, max(0.0, float(telemetry)))
    score = (
        ioc_signal * 0.25
        + evidence_signal * 0.25
        + min(1.0, float(cwss.get("score", 0.0)) / 10) * 0.2
        + label_signal * 0.2
        + telemetry_signal * 0.1
    )
    return round(min(1.0, max(0.0, score)), 4)