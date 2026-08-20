from __future__ import annotations

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.orchestrator import build_orchestrator_graph
from quallki_agentic.qml_stub import infer_with_metadata
from quallki_agentic.telemetry.ingestion import TelemetryIngestion


def run_healthcare_demo_scenario(scenario_key: str) -> dict[str, object]:
    if scenario_key not in HOSPITAL_DEMO_CASES:
        raise ValueError(f"Unknown scenario: {scenario_key}")

    scenario = HOSPITAL_DEMO_CASES[scenario_key]
    message = str(scenario["message"])

    telemetry = TelemetryIngestion()
    raw = telemetry.ingest_alert(message, source_ip=str(scenario["source_ip"]))
    qml_result = infer_with_metadata(
        {"message": message, "logs": list(scenario.get("logs", []))}
    )
    label = qml_result["label"]

    payload = {
        "message": message,
        "scenario": scenario_key,
        "asset_type": scenario.get("asset_type"),
        "contains_phi": scenario.get("contains_phi", False),
        "clinical_impact": scenario.get("clinical_impact", "medium"),
        "source_ip": str(raw.get("source_ip", "0.0.0.0")),
        "telemetry_signals": {"signal_strength": 0.5},
        "logs": list(scenario.get("logs", [])),
        "compliance_context": {
            "hipaa_applicable": True,
            "gdpr_applicable": False,
            "iso_scope": False,
            "soc2_scope": False,
            "nis2_applicable": False,
        },
    }

    result = build_orchestrator_graph().invoke(payload)
    return {
        "scenario_key": scenario_key,
        "scenario": scenario,
        "label": label,
        "confidence": result.get("alert_object", {}).get("composite_confidence", 0.0),
        "qml_backend": result.get("alert_object", {}).get("qml_backend", qml_result["backend"]),
        "result": result,
        "payload": payload,
        "logs": payload["logs"],
    }
