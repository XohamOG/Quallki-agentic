from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class TriageVerdict(BaseModel):
    incident_id: str = Field(description="Unique parent incident ID or cluster ID")

    # 1. Actionable Decision
    action: Literal["AUTO_CLOSE_FALSE_POSITIVE", "INVESTIGATE_LOW", "ESCALATE_HIGH", "CONTAIN_CRITICAL"]
    assigned_priority: Literal["P1", "P2", "P3", "P4"]

    # 2. Reasoning & Scope
    threat_hypothesis: str = Field(
        description="Concise synthesis of what the attacker is attempting"
    )
    blast_radius: Literal["Isolated_Host", "Subnet_VLAN", "Domain_Wide", "External_Perimeter"]
    affected_critical_assets: List[str] = Field(
        description="List of high-value systems at immediate risk"
    )

    # 3. False Positive Justification (Required if auto-closed)
    auto_close_rationale: Optional[str] = Field(
        default=None,
        description="Defensible justification why this alert is benign noise"
    )

    # 4. Downstream Dispatch Plan
    required_specialists: List[Literal["ThreatIntelAgent", "ResponseAgent", "ForensicsAgent", "ComplianceAgent"]] = Field(
        description="Which agents the Orchestrator must invoke"
    )
    recommended_containment: Optional[str] = Field(
        default=None,
        description="Specific mitigation command for the Response Agent"
    )

    # 5. Human-in-the-Loop Gate
    requires_human_signoff: bool = Field(
        description="True if destructive actions (host shutdown, IP block) are planned"
    )
    human_executive_brief: Optional[str] = Field(
        default=None,
        description="3-sentence summary for the SOC lead approval modal"
    )
