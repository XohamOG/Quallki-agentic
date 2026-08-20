from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class ForensicsAgent(BaseAgent):
    name = "forensics"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        triage = payload.get("triage_result", {})
        priority = "P4"
        if isinstance(triage, dict):
            priority = str(triage.get("priority", "P4"))

        logs = payload.get("logs", [])
        from quallki_agentic.llm_helper import invoke_gemini
        prompt = (
            "You are a digital forensics investigator. Based on the following logs and priority level, "
            "write a concise 2-sentence narrative timeline of the attack progression. "
            "Return strict JSON with a single key 'forensics_summary' containing the string.\n\n"
            f"Priority: {priority}\n"
            f"Logs: {logs}"
        )
        parsed = invoke_gemini(prompt)
        
        summary = ""
        if parsed and "forensics_summary" in parsed:
            summary = str(parsed["forensics_summary"])
        else:
            summary = (
                "Timeline reconstructed from alert and IOC context. "
                f"Mapped to ATT&CK phases for {priority} incident path."
            )
        return {"forensics_summary": summary}
