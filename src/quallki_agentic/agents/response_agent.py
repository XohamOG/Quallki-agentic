from __future__ import annotations

from quallki_agentic.agents.base_agent import BaseAgent


class ResponseAgent(BaseAgent):
    name = "response"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        alert = payload.get("alert_object", {})
        ip = "0.0.0.0"
        asset_type = "unknown"
        contains_phi = False
        if isinstance(alert, dict):
            ip = str(alert.get("source_ip", "0.0.0.0"))
            asset_type = str(alert.get("asset_type", "unknown"))
            contains_phi = bool(alert.get("contains_phi", False))

        actions = []
        from quallki_agentic.llm_helper import invoke_gemini
        prompt = (
            "You are a SOC responder. Given the alert context, generate 3-5 specific, actionable containment steps. "
            "Return strict JSON with a single key 'response_actions' containing a list of strings.\n\n"
            f"Alert ID: {alert.get('alert_id')}\n"
            f"Message: {alert.get('message')}\n"
            f"IP: {ip}\n"
            f"Asset Type: {asset_type}\n"
            f"Contains PHI: {contains_phi}\n"
            f"Attack Vector: {alert.get('analysis', {}).get('attack_vector', 'unknown')}\n"
        )
        parsed = invoke_gemini(prompt)
        if parsed and isinstance(parsed.get("response_actions"), list):
            actions = [str(a) for a in parsed["response_actions"]]
        else:
            actions = [
                f"Block source IP {ip} at PEP/firewall boundary.",
                "Revoke active auth tokens for impacted identity scope.",
                "Trigger host isolation through endpoint control with clinical safety validation.",
            ]
            if asset_type in {"ehr_server", "pacs"}:
                actions.append("Notify clinical operations lead before service restart to avoid patient care disruption.")
            if contains_phi:
                actions.append("Start PHI breach impact assessment and preserve legal/audit evidence chain.")
                
        return {"response_actions": actions}
