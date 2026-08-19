from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.orchestrator.schema import AlertObject, now_iso


class DetectionAgent(BaseAgent):
    name = "detection"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        message = str(payload.get("message", ""))
        source_ip = str(payload.get("source_ip", "0.0.0.0"))
        alert_id = str(payload.get("alert_id", "alert-auto"))
        event_time = str(payload.get("event_time", now_iso()))
        qml_label = str(payload.get("qml_label", "unknown"))
        qml_confidence = float(payload.get("qml_confidence", 0.5))
        contains_phi = bool(payload.get("contains_phi", False))
        clinical_impact = str(payload.get("clinical_impact", "medium"))
        asset_type = str(payload.get("asset_type", "unknown"))
        iocs = [token for token in message.replace(",", " ").split() if "." in token or token.startswith("CVE-")]

        alert = AlertObject(
            alert_id=alert_id,
            source_ip=source_ip,
            event_time=event_time,
            message=message,
            qml_label=qml_label,
            qml_confidence=qml_confidence,
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
        return {"alert_object": alert_dict, "iocs": iocs}
