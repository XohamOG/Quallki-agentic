from __future__ import annotations

import json
import os

from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.config import Settings


class TriageAgent(BaseAgent):
    name = "triage"

    def __init__(self) -> None:
        self._settings = Settings.from_env()

    def _heuristic_triage(self, label: str, confidence: float) -> dict[str, object]:
        label_map = {
            "hulk": "dos",
            "slowloris": "dos",
            "discov": "recon",
            "nmap": "recon",
            "ransac": "malware",
            "ssh": "brute_force",
            "baseline": "normal",
        }
        label = label_map.get(label, label)

        priority = "P4"
        route = "auto_close"
        reasoning = "Low confidence or low impact pattern."
        auto_close = True

        if label in {"malware", "dos"} and confidence >= 0.75:
            priority = "P1"
            route = "response_path"
            reasoning = "High-impact attack pattern with strong classifier confidence."
            auto_close = False
        elif label in {"recon", "brute_force"} and confidence >= 0.65:
            priority = "P2"
            route = "investigate_path"
            reasoning = "Suspicious reconnaissance or credential abuse requiring investigation."
            auto_close = False
        elif confidence >= 0.6:
            priority = "P3"
            route = "investigate_path"
            reasoning = "Moderate confidence anomaly; requires analyst review."
            auto_close = False

        return {
            "priority": priority,
            "confidence": confidence,
            "reasoning": reasoning,
            "auto_close": auto_close,
            "route": route,
        }

    def _gemini_triage(
        self,
        message: str,
        label: str,
        confidence: float,
        source_ip: str,
    ) -> dict[str, object] | None:
        if self._settings.llm_provider.lower() != "gemini":
            return None
        if not os.getenv("GEMINI_API_KEY"):
            return None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=self._settings.gemini_model,
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0,
            )
            prompt = (
                "You are a SOC Triage Agent. Return strict JSON only with keys: "
                "priority, confidence, reasoning, auto_close, route. "
                "Rules: priority in [P1,P2,P3,P4], route in [response_path,investigate_path,auto_close]. "
                "Use CVSS-like impact logic and avoid verbose output.\n\n"
                f"Alert message: {message}\n"
                f"Detected label: {label}\n"
                f"Model confidence: {confidence:.4f}\n"
                f"Source IP: {source_ip}\n"
            )
            content = llm.invoke(prompt).content
            raw = str(content).strip()
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                return None
            parsed = json.loads(raw[start : end + 1])

            priority = str(parsed.get("priority", "P3"))
            route = str(parsed.get("route", "investigate_path"))
            if priority not in {"P1", "P2", "P3", "P4"}:
                priority = "P3"
            if route not in {"response_path", "investigate_path", "auto_close"}:
                route = "investigate_path"

            llm_conf = float(parsed.get("confidence", confidence))
            return {
                "priority": priority,
                "confidence": max(0.0, min(1.0, llm_conf)),
                "reasoning": str(parsed.get("reasoning", "LLM triage completed.")),
                "auto_close": bool(parsed.get("auto_close", route == "auto_close")),
                "route": route,
            }
        except Exception:
            return None

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        alert = payload.get("alert_object", {})
        if not isinstance(alert, dict):
            alert = {}

        label = str(alert.get("qml_label", "unknown")).lower()
        confidence = float(alert.get("qml_confidence", 0.5))
        message = str(alert.get("message", ""))
        source_ip = str(alert.get("source_ip", "0.0.0.0"))

        triage = self._gemini_triage(message, label, confidence, source_ip)
        if triage is None:
            triage = self._heuristic_triage(label, confidence)

        return {
            "triage_result": {
                "priority": triage["priority"],
                "confidence": triage["confidence"],
                "reasoning": triage["reasoning"],
                "auto_close": triage["auto_close"],
            },
            "route": triage["route"],
        }
