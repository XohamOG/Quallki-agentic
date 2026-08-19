from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.healthcare import summarize_checklist


class ComplianceAgent(BaseAgent):
    name = "compliance"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        checklist, summary = summarize_checklist(payload)
        return {
            "compliance_note": summary,
            "compliance_checklist": checklist,
        }
