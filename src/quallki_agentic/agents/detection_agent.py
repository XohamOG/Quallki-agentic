from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.log_analyzer import analyze
from quallki_agentic.orchestrator.schema import AlertObject, now_iso
from quallki_agentic.qml_stub import infer_with_metadata
from quallki_agentic.scoring import aggregate_confidence, score_cwss


class DetectionAgent(BaseAgent):
    name = "detection"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        message = str(payload.get("message", ""))
        source_ip = str(payload.get("source_ip", "0.0.0.0"))
        alert_id = str(payload.get("alert_id", "alert-auto"))
        event_time = str(payload.get("event_time", now_iso()))
        contains_phi = bool(payload.get("contains_phi", False))
        clinical_impact = str(payload.get("clinical_impact", "medium"))
        asset_type = str(payload.get("asset_type", "unknown"))

        if source_ip == "0.0.0.0" and not message and payload.get("logs"):
            from quallki_agentic.llm_helper import invoke_gemini
            prompt = (
                "You are a SOC parser. Extract the following from the raw logs provided below. "
                "Return strict JSON with keys: message, source_ip, asset_type, clinical_impact, contains_phi (boolean). "
                "Guess impact (low/medium/high/critical) and asset_type (e.g. ehr_server, pacs, endpoint) from context.\n\n"
                f"Logs: {payload['logs']}"
            )
            parsed = invoke_gemini(prompt)
            if parsed:
                message = str(parsed.get("message", message))
                source_ip = str(parsed.get("source_ip", source_ip))
                asset_type = str(parsed.get("asset_type", asset_type))
                clinical_impact = str(parsed.get("clinical_impact", clinical_impact))
                contains_phi = bool(parsed.get("contains_phi", contains_phi))
                # Update payload so downstream components get the enriched data
                payload["message"] = message
                payload["source_ip"] = source_ip
                payload["asset_type"] = asset_type
                payload["clinical_impact"] = clinical_impact
                payload["contains_phi"] = contains_phi
        qml_result = infer_with_metadata(payload)
        qml_label = str(qml_result.get("label", "unknown"))
        analysis = analyze(payload, qml_label)
        iocs = analysis["iocs"]
        cwss = score_cwss(qml_label, analysis, clinical_impact)
        composite_confidence = aggregate_confidence(
            qml_label, analysis, cwss, payload.get("telemetry_signals")
        )

        alert = AlertObject(
            alert_id=alert_id,
            source_ip=source_ip,
            event_time=event_time,
            message=message,
            qml_label=qml_label,
            iocs=iocs,
            metadata={
                "telemetry_window": "1s",
                "domain": "healthcare",
                "asset_type": asset_type,
                "clinical_impact": clinical_impact,
            },
        )
        alert_dict = alert.__dict__
        alert_dict["contains_phi"] = contains_phi
        alert_dict["clinical_impact"] = clinical_impact
        alert_dict["asset_type"] = asset_type
        alert_dict["composite_confidence"] = composite_confidence
        alert_dict["analysis"] = analysis
        alert_dict["cwss"] = cwss
        alert_dict["qml_backend"] = qml_result.get("backend", "unknown")
        alert_dict["classical_label"] = qml_result.get("classical_label", "unknown")
        return {"alert_object": alert_dict, "iocs": iocs}
