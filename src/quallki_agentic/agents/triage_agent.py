from __future__ import annotations

import os
import uuid
from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.config import Settings
from quallki_agentic.telemetry.schemas import TriageVerdict


class TriageAgent(BaseAgent):
    name = "triage"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        settings = Settings.from_env()

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

        prompt = f"""
        You are the Tier-2 Triage Agent in QUAL-KĪ SOC.
        Analyze the following security telemetry and determine the TriageVerdict:
        - QML Label: {label}
        - Composite Confidence: {confidence:.2f}
        - CWSS Score: {cwss_score:.2f}
        - Attack Vector: {attack_vector}
        - Clinical Impact: {clinical_impact}
        - Evidence: {analysis.get('evidence', [])}
        - Affected Assets: {affected_assets}
        - Message: {payload.get('message', '')}
        - Logs: {payload.get('logs', [])}
        
        Generate the incident ID (e.g., INC-YYYY-XXX), formulate a threat hypothesis, determine if it's a false positive, and specify exactly which specialist agents to route to.
        """

        verdict: TriageVerdict | None = None
        
        # Try NVIDIA first
        llm = None
        if os.getenv("NVIDIA_API_KEY"):
            try:
                from langchain_nvidia_ai_endpoints import ChatNVIDIA
                llm = ChatNVIDIA(
                    model="nvidia/nemotron-3-ultra-550b-a55b",
                    nvidia_api_key=os.environ["NVIDIA_API_KEY"],
                    temperature=0.0
                )
            except Exception as e:
                print(f"Failed to load NVIDIA LLM in Triage: {e}")
                llm = None

        # Fallback to Gemini
        if not llm and settings.use_gemini and os.getenv("GEMINI_API_KEY"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=os.environ["GEMINI_API_KEY"],
                    temperature=0.0,
                )
            except Exception as e:
                print(f"Failed to load Gemini LLM in Triage: {e}")
                llm = None

        if llm:
            try:
                structured_llm = llm.with_structured_output(TriageVerdict)
                verdict = structured_llm.invoke(prompt)
            except Exception as e:
                print(f"Triage LLM extraction error: {e}")

        if verdict:
            # Route logic based on verdict action
            route = "investigate_path"
            if verdict.action in ["ESCALATE_HIGH", "CONTAIN_CRITICAL"]:
                route = "response_path"
            elif verdict.action == "AUTO_CLOSE_FALSE_POSITIVE":
                route = "auto_close"
                
            return {
                "triage_result": {
                    "incident_id": verdict.incident_id,
                    "priority": verdict.assigned_priority,
                    "confidence": confidence,
                    "action": verdict.action,
                    "threat_hypothesis": verdict.threat_hypothesis,
                    "blast_radius": verdict.blast_radius,
                    "affected_critical_assets": verdict.affected_critical_assets,
                    "auto_close_rationale": verdict.auto_close_rationale,
                    "required_specialists": verdict.required_specialists,
                    "recommended_containment": verdict.recommended_containment,
                    "requires_human_signoff": verdict.requires_human_signoff,
                    "human_executive_brief": verdict.human_executive_brief,
                    "reasoning_backend": "gemini_structured"
                },
                "route": route,
            }

        # Fallback deterministic
        priority = "P1" if cwss_score >= 6 else "P2"
        route = "response_path" if priority == "P1" else "investigate_path"
        return {
            "triage_result": {
                "incident_id": f"INC-{uuid.uuid4().hex[:6]}",
                "priority": priority,
                "confidence": confidence,
                "action": "CONTAIN_CRITICAL" if priority == "P1" else "INVESTIGATE_LOW",
                "threat_hypothesis": f"Fallback hypothesis for {attack_vector}",
                "blast_radius": "Isolated_Host",
                "affected_critical_assets": [str(a) for a in affected_assets],
                "auto_close_rationale": None,
                "required_specialists": ["ThreatIntelAgent", "ResponseAgent"],
                "recommended_containment": "Isolate affected host",
                "requires_human_signoff": True,
                "human_executive_brief": f"Fallback alert for {label} - {cwss_score}",
                "reasoning_backend": "deterministic_fallback"
            },
            "route": route,
        }
