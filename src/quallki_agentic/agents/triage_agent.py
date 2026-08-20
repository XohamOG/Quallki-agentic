from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class TriageAgent(BaseAgent):
    name = "triage"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        alert = payload.get("alert_object", {})
        if not isinstance(alert, dict):
            alert = {}

        label = str(alert.get("qml_label", "unknown")).lower()
        confidence = float(alert.get("composite_confidence", 0.0))
        cwss = alert.get("cwss", {})
        cwss_score = float(cwss.get("score", 0.0)) if isinstance(cwss, dict) else 0.0
        analysis = alert.get("analysis", {})
        attack_vector = str(analysis.get("attack_vector", "unknown")) if isinstance(analysis, dict) else "unknown"
        clinical_impact = str(alert.get("clinical_impact", "medium")).lower()
        affected_assets = analysis.get("affected", [alert.get("asset_type", "unknown")]) if isinstance(analysis, dict) else ["unknown"]
        if not isinstance(affected_assets, list):
            affected_assets = [affected_assets]

        if (clinical_impact == "critical" and confidence >= 0.8) or cwss_score >= 9:
            priority, route = "P0", "response_path"
        elif confidence >= 0.65 or cwss_score >= 6:
            priority, route = "P1", "response_path"
        else:
            priority, route = "P2", "investigate_path"
        auto_close = False
        reasoning = (
            f"{priority} assigned from composite confidence {confidence:.2f}, "
            f"CWSS-like score {cwss_score:.2f}, {attack_vector} vector, and {clinical_impact} clinical impact."
        )
        fixes = {
            "endpoint": ["Isolate affected endpoint", "Preserve encrypted-file and process telemetry"],
            "web application": ["Block malicious request source", "Review and parameterize affected queries"],
            "identity": ["Lock or reset affected credentials", "Review authentication logs and MFA posture"],
        }.get(attack_vector, ["Validate the alert and preserve relevant logs", "Apply targeted containment after confirmation"])

        return {
            "triage_result": {
                "priority": priority,
                "confidence": confidence,
                "reasoning": reasoning,
                "auto_close": auto_close,
                "affected_assets": [str(asset) for asset in affected_assets],
                "impact": clinical_impact,
                "recommended_fixes": fixes,
            },
            "route": route,
        }
