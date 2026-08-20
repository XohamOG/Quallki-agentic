from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.healthcare.compliance import assess_compliance


class ComplianceAgent(BaseAgent):
    name = "compliance"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        checklist, summary, assessment = assess_compliance(payload)
        
        from quallki_agentic.llm_helper import invoke_gemini
        logs = payload.get("logs", [])
        prompt = (
            "You are a healthcare compliance expert and auditor. Based on the logs below, identify relevant compliance controls "
            "that might have been violated or need checking (e.g., HIPAA Security Rule, NIST CSF, ISO 27001). "
            "Provide a detailed, explanatory summary explaining *why* these controls apply based on the specific attack vector, assets, and SIEM logs provided. "
            "Make sure your explanation is thorough, highlighting the exact evidence that triggered the control applicability. "
            "Return strict JSON with a single key 'suggestions' containing your detailed explanatory string.\n\n"
            f"Logs: {logs}"
        )
        parsed = invoke_gemini(prompt)
        if parsed and "suggestions" in parsed:
            summary += f" LLM Suggestion: {parsed['suggestions']}"
            
        return {
            "compliance_note": summary,
            "compliance_checklist": checklist,
            "compliance_assessment": assessment,
        }
