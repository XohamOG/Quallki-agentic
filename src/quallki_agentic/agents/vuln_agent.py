from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class VulnAssessmentAgent(BaseAgent):
    name = "vuln_assessment"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        return {
            "vulnerability_report": {
                "top_risk": "Internet-exposed legacy service",
                "recommendation": "Patch critical CVEs and enforce segmentation policy.",
            }
        }
