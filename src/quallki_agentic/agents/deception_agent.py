from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class DeceptionAgent(BaseAgent):
    name = "deception"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        return {
            "deception_plan": [
                "Deploy medium-interaction SSH honeypot in decoy subnet.",
                "Mirror attacker command telemetry to threat intel pipeline.",
            ]
        }
