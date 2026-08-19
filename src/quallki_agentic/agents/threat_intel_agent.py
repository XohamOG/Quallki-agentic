from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class ThreatIntelAgent(BaseAgent):
    name = "threat_intel"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        iocs = payload.get("iocs", [])
        if not isinstance(iocs, list):
            iocs = []

        techniques: list[str] = []
        campaigns: list[str] = []
        cves: list[str] = []

        for ioc in iocs:
            token = str(ioc)
            if token.startswith("CVE-"):
                cves.append(f"https://nvd.nist.gov/vuln/detail/{token}")
            if token.count(".") == 3:
                techniques.append("T1046")

        if techniques:
            campaigns.append("Potential intrusion set requiring ATT&CK correlation")

        return {
            "threat_intel_result": {
                "attack_techniques": sorted(set(techniques)) or ["T1595"],
                "related_campaigns": campaigns,
                "cve_links": cves,
            }
        }
