from __future__ import annotations

from typing import Any

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.healthcare.attack_simulator import AttackSimulator
from quallki_agentic.orchestrator import build_orchestrator_graph


def run_alert_payload(payload: dict[str, Any], scenario: dict[str, Any] | None = None) -> dict[str, object]:
    """Run an arbitrary normalized alert through the compiled LangGraph."""
    if not isinstance(payload, dict):
        raise TypeError("Alert payload must be a JSON object")
    scenario = scenario or {
        "title": "Live alert",
        "message": payload.get("message", ""),
        "asset_type": payload.get("asset_type", "unknown"),
        "contains_phi": payload.get("contains_phi", False),
        "clinical_impact": payload.get("clinical_impact", "medium"),
        "source_ip": payload.get("source_ip", "unknown"),
    }
    workflow_trace: list[dict[str, object]] = []
    result: dict[str, object] = {}
    for update in build_orchestrator_graph().stream(payload, stream_mode="updates"):
        if not isinstance(update, dict):
            continue
        for node_name, node_output in update.items():
            output = node_output if isinstance(node_output, dict) else {"value": node_output}
            workflow_trace.append({"node": node_name, "output": output})
            result.update(output)

    alert = result.get("alert_object", {})
    label = str(alert.get("qml_label", "unknown")) if isinstance(alert, dict) else "unknown"
    qml_backend = str(alert.get("qml_backend", "unknown")) if isinstance(alert, dict) else "unknown"
    return {
        "scenario_key": str(payload.get("scenario", "live_alert")),
        "scenario": scenario,
        "label": label,
        "confidence": alert.get("composite_confidence", 0.0) if isinstance(alert, dict) else 0.0,
        "qml_backend": qml_backend,
        "result": result,
        "payload": payload,
        "logs": payload.get("logs", []),
        "workflow_trace": workflow_trace,
    }


def run_healthcare_demo_scenario(scenario_key: str) -> dict[str, object]:
    if scenario_key not in HOSPITAL_DEMO_CASES:
        raise ValueError(f"Unknown scenario: {scenario_key}")
    payload = AttackSimulator().simulate(scenario_key)
    return run_alert_payload(payload, HOSPITAL_DEMO_CASES[scenario_key])
