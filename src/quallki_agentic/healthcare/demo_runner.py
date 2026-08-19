from __future__ import annotations

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.orchestrator import build_orchestrator_graph
from quallki_agentic.quantum.ensemble import QuantumEnsembleClient
from quallki_agentic.telemetry.ingestion import TelemetryIngestion


def run_healthcare_demo_scenario(scenario_key: str) -> dict[str, object]:
    if scenario_key not in HOSPITAL_DEMO_CASES:
        raise ValueError(f"Unknown scenario: {scenario_key}")

    scenario = HOSPITAL_DEMO_CASES[scenario_key]
    message = str(scenario["message"])

    telemetry = TelemetryIngestion()
    detector = QuantumEnsembleClient()

    raw = telemetry.ingest_alert(message, source_ip=str(scenario["source_ip"]))
    label, confidence = detector.infer_label(message)

    payload = {
        "message": message,
        "scenario": scenario_key,
        "asset_type": scenario.get("asset_type"),
        "contains_phi": scenario.get("contains_phi", False),
        "clinical_impact": scenario.get("clinical_impact", "medium"),
        "source_ip": str(raw.get("source_ip", "0.0.0.0")),
        "qml_label": label,
        "qml_confidence": confidence,
    }

    result = build_orchestrator_graph().invoke(payload)
    return {
        "scenario_key": scenario_key,
        "scenario": scenario,
        "label": label,
        "confidence": confidence,
        "result": result,
        "payload": payload,
    }
