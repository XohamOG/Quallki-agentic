from __future__ import annotations

import os
from pydantic import BaseModel, Field
from typing import List, Any
from quallki_agentic.agents.base_agent import BaseAgent
from quallki_agentic.telemetry.cwe_mapping import ATTACK_TO_CWE_MAP
from quallki_agentic.telemetry.cwss_engine import CWSSFactors, calculate_cwss
from quallki_agentic.config import Settings


class CWEAssessmentOutput(BaseModel):
    selected_cwe_id: str = Field(description="The primary CWE ID (e.g., 'CWE-89')")
    cwe_name: str = Field(description="Full name of the selected CWE")
    technical_justification: str = Field(description="Why this CWE caused the alert")
    cwss_factors: CWSSFactors = Field(description="Discrete factors for scoring engine")


class ThreatIntelAgent(BaseAgent):
    name = "threat_intel"

    def run(self, payload: dict[str, object]) -> dict[str, object]:
        settings = Settings.from_env()

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
                
        # Phase 1: Determine Technique (Fallback logic)
        for ioc in iocs:
            token = str(ioc)
            if token.count(".") == 3:
                if "T1046" not in techniques: techniques.append("T1046")
        if not techniques:
            techniques = ["T1190"] # default

        technique_id = techniques[0]
        
        candidates = ATTACK_TO_CWE_MAP.get(technique_id, [
            {"cwe_id": "CWE-699", "name": "Software Development Weakness", "capec": "N/A"}
        ])

        source_ip = payload.get("source_ip", "unknown")
        asset_type = payload.get("asset_type", "unknown")
        message = payload.get("message", "N/A")

        prompt = f"""
        You are the Threat Intel and Vulnerability Assessment Agent in QUAL-KĪ SOC.
        Analyze the following security telemetry:
        - Asset Type: {asset_type}
        - Logs/Message: {message}
        - Network Source IP: {source_ip}
        - MITRE ATT&CK Technique: {technique_id}
        - IOCs: {iocs}

        Candidate CWEs from MITRE Knowledge Base:
        {candidates}

        Task 1: Select the single most applicable CWE and assign standard CWSS categorical factors.
        """

        final_cwss_score = 0.0
        agent_decision = None
        
        # Try NVIDIA first
        llm = None
        if os.getenv("NVIDIA_API_KEY"):
            try:
                from langchain_nvidia_ai_endpoints import ChatNVIDIA
                llm = ChatNVIDIA(
                    model="nvidia/nemotron-3-ultra-550b-a55b",
                    nvidia_api_key=os.environ["NVIDIA_API_KEY"],
                    temperature=0.0
                )
            except Exception as e:
                print(f"Failed to load NVIDIA LLM in Threat Intel: {e}")
                llm = None

        # Fallback to Gemini
        if not llm and settings.use_gemini and os.getenv("GEMINI_API_KEY"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=os.environ["GEMINI_API_KEY"],
                    temperature=0.0,
                )
            except Exception as e:
                print(f"Failed to load Gemini LLM in Threat Intel: {e}")
                llm = None

        if llm:
            try:
                structured_llm = llm.with_structured_output(CWEAssessmentOutput)
                agent_decision = structured_llm.invoke(prompt)
            except Exception as e:
                print(f"Failed structured LLM call: {e}")

        top_risk = "Internet-exposed legacy service"
        cwss_score = 0.0
        cwe_id = None
        if agent_decision:
            cwss_score = calculate_cwss(agent_decision.cwss_factors)
            top_risk = f"{agent_decision.selected_cwe_id}: {agent_decision.cwe_name}"
            cwe_id = agent_decision.selected_cwe_id

        return {
            "threat_intel_result": {
                "attack_techniques": techniques,
                "related_campaigns": campaigns,
                "cve_links": cves,
            },
            "vulnerability_report": {
                "top_risk": top_risk,
                "cwss_score": cwss_score,
                "cwe_id": cwe_id,
            }
        }
