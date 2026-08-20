from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.healthcare.compliance import assess_compliance


class ComplianceAgent(BaseAgent):
    name = "compliance"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        checklist, summary, assessment = assess_compliance(payload)
        return {
            "compliance_note": summary,
            "compliance_checklist": checklist,
            "compliance_assessment": assessment,
        }
