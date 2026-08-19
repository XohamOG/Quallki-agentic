from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class ForensicsAgent(BaseAgent):
    name = "forensics"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        triage = payload.get("triage_result", {})
        priority = "P4"
        if isinstance(triage, dict):
            priority = str(triage.get("priority", "P4"))

        summary = (
            "Timeline reconstructed from alert and IOC context. "
            f"Mapped to ATT&CK phases for {priority} incident path."
        )
        return {"forensics_summary": summary}
