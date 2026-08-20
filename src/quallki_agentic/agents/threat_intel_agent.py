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
                
        from quallki_agentic.llm_helper import invoke_gemini
        prompt = (
            "You are a threat intelligence analyst. Based on these IOCs, suggest 1-3 likely MITRE ATT&CK techniques "
            "and any related campaigns. Return strict JSON with keys: attack_techniques (list of strings, e.g., ['T1046']), "
            "related_campaigns (list of strings).\n\n"
            f"IOCs: {iocs}"
        )
        parsed = invoke_gemini(prompt)
        if parsed:
            techniques = [str(t) for t in parsed.get("attack_techniques", [])]
            campaigns = [str(c) for c in parsed.get("related_campaigns", [])]
        else:
            for ioc in iocs:
                token = str(ioc)
                if token.count(".") == 3:
                    if "T1046" not in techniques: techniques.append("T1046")
            if techniques:
                campaigns.append("Potential intrusion set requiring ATT&CK correlation")

        return {
            "threat_intel_result": {
                "attack_techniques": sorted(set(techniques)) or ["T1595"],
                "related_campaigns": campaigns,
                "cve_links": cves,
            }
        }
