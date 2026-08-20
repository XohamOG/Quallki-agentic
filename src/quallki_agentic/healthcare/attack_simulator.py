from __future__ import annotations

from typing import Any

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.telemetry.ingestion import TelemetryIngestion


class AttackSimulator:
    """Generate safe, deterministic telemetry for a selected attack scenario."""

    def __init__(self, telemetry: TelemetryIngestion | None = None) -> None:
        self.telemetry = telemetry or TelemetryIngestion()

    def simulate(self, scenario_key: str) -> dict[str, Any]:
        if scenario_key not in HOSPITAL_DEMO_CASES:
            raise ValueError(f"Unknown scenario: {scenario_key}")

        scenario = HOSPITAL_DEMO_CASES[scenario_key]
        message = str(scenario["message"])
        raw = self.telemetry.ingest_alert(
            message,
            source_ip=str(scenario["source_ip"]),
        )
        logs = [str(log) for log in scenario.get("logs", [])]
        return {
            "message": message,
            "scenario": scenario_key,
            "asset_type": scenario.get("asset_type", "unknown"),
            "contains_phi": bool(scenario.get("contains_phi", False)),
            "clinical_impact": scenario.get("clinical_impact", "medium"),
            "source_ip": str(raw.get("source_ip", "0.0.0.0")),
            "event_time": logs[0].split(" ", 1)[0] if logs else None,
            "logs": logs,
            "telemetry_signals": {"signal_strength": 0.5},
            "compliance_context": {
                "hipaa_applicable": True,
                "gdpr_applicable": False,
                "iso_scope": False,
                "soc2_scope": False,
                "nis2_applicable": False,
            },
            "simulation": {
                "enabled": True,
                "scenario_key": scenario_key,
                "source": "synthetic_healthcare_scenario",
                "side_effects": "none",
            },
        }
