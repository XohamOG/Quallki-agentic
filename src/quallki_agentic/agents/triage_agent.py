from __future__ import annotations

import json
import os

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.config import Settings


class TriageAgent(BaseAgent):
    name = "triage"

    def __init__(self) -> None:
        self._settings = Settings.from_env()

    def _gemini_reasoning(
        self,
        label: str,
        confidence: float,
        cwss_score: float,
        attack_vector: str,
        clinical_impact: str,
        evidence: list[str],
        affected_assets: list[object],
    ) -> dict[str, object] | None:
        from quallki_agentic.llm_helper import invoke_gemini

        prompt = (
            "You are a healthcare SOC reasoning specialist. Return strict JSON only with "
            "keys reasoning and recommended_fixes. Do not change priority, route, or confidence. "
            "Do not claim compliance or certainty. Keep reasoning under 45 words and provide "
            "at most 4 concise fixes. Never recommend disruptive clinical action without human approval.\n\n"
            f"QML label: {label}\n"
            f"Composite confidence: {confidence:.4f}\n"
            f"CWSS-like score: {cwss_score:.2f}\n"
            f"Attack vector: {attack_vector}\n"
            f"Clinical impact: {clinical_impact}\n"
            f"Evidence: {evidence}\n"
            f"Affected assets: {affected_assets}\n"
        )
        
        parsed = invoke_gemini(prompt)
        if not parsed:
            return None
            
        fixes = parsed.get("recommended_fixes", [])
        if not isinstance(fixes, list):
            fixes = []
        return {
            "reasoning": str(parsed.get("reasoning", "Gemini reasoning completed.")),
            "recommended_fixes": [str(item) for item in fixes[:4]],
            "backend": "gemini",
        }

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
        gemini = self._gemini_reasoning(
            label,
            confidence,
            cwss_score,
            attack_vector,
            clinical_impact,
            analysis.get("evidence", []) if isinstance(analysis, dict) else [],
            [str(asset) for asset in affected_assets],
        )
        reasoning_backend = "deterministic"
        if gemini:
            reasoning = f"{reasoning} Gemini analyst note: {gemini['reasoning']}"
            if gemini["recommended_fixes"]:
                fixes = gemini["recommended_fixes"]
            reasoning_backend = "deterministic+gemini"

        return {
            "triage_result": {
                "priority": priority,
                "confidence": confidence,
                "reasoning": reasoning,
                "auto_close": auto_close,
                "affected_assets": [str(asset) for asset in affected_assets],
                "impact": clinical_impact,
                "recommended_fixes": fixes,
                "reasoning_backend": reasoning_backend,
            },
            "route": route,
        }
