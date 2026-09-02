from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

class CWSSFactors(BaseModel):
    """Categorical factors extracted by LLM from telemetry and system context."""
    # Base Finding Group
    technical_impact: Literal["Critical", "High", "Medium", "Low", "None"] = Field(
        description="Severity of damage if exploited"
    )
    acquired_privilege: Literal["Administrator", "RegularUser", "Guest", "None"] = Field(
        description="Privilege level an attacker gains"
    )
    finding_confidence: Literal["Confirmed", "High", "Medium", "Low"] = Field(
        description="Confidence in detection accuracy"
    )

    # Attack Surface Group
    required_privilege: Literal["None", "Guest", "RegularUser", "Administrator"] = Field(
        description="Privileges attacker needed before launching attack"
    )
    access_vector: Literal["Internet", "Intranet", "PrivateNetwork", "Local", "Physical"] = Field(
        description="Network proximity needed to reach vulnerability"
    )
    authentication_strength: Literal["None", "Weak", "Moderate", "Strong"] = Field(
        description="Strength of authentication bypassed or exploited"
    )

    # Environmental Group
    business_impact: Literal["Critical", "High", "Medium", "Low", "None"] = Field(
        description="Impact on enterprise operations / revenue"
    )
    likelihood_of_exploit: Literal["High", "Medium", "Low", "None"] = Field(
        description="Active exploit kits, automation, or public tools in the wild"
    )


# MITRE CWSS v1.0.1 Official Factor Weights
WEIGHTS = {
    "technical_impact": {"Critical": 1.0, "High": 0.9, "Medium": 0.6, "Low": 0.3, "None": 0.0},
    "acquired_privilege": {"Administrator": 1.0, "RegularUser": 0.7, "Guest": 0.4, "None": 0.0},
    "finding_confidence": {"Confirmed": 1.0, "High": 0.9, "Medium": 0.7, "Low": 0.5},

    "required_privilege": {"None": 1.0, "Guest": 0.85, "RegularUser": 0.7, "Administrator": 0.4},
    "access_vector": {"Internet": 1.0, "Intranet": 0.85, "PrivateNetwork": 0.7, "Local": 0.5, "Physical": 0.2},
    "authentication_strength": {"None": 1.0, "Weak": 0.8, "Moderate": 0.6, "Strong": 0.4},

    "business_impact": {"Critical": 1.0, "High": 0.9, "Medium": 0.6, "Low": 0.3, "None": 0.0},
    "likelihood_of_exploit": {"High": 1.0, "Medium": 0.7, "Low": 0.3, "None": 0.0}
}

def calculate_cwss(factors: CWSSFactors) -> float:
    """Calculates official normalized CWSS v1.0.1 score (0 to 100)."""
    # Sub-score calculations
    base = (
        WEIGHTS["technical_impact"][factors.technical_impact] * 0.5 +
        WEIGHTS["acquired_privilege"][factors.acquired_privilege] * 0.3 +
        WEIGHTS["finding_confidence"][factors.finding_confidence] * 0.2
    )

    attack_surface = (
        WEIGHTS["required_privilege"][factors.required_privilege] * 0.4 +
        WEIGHTS["access_vector"][factors.access_vector] * 0.4 +
        WEIGHTS["authentication_strength"][factors.authentication_strength] * 0.2
    )

    environmental = (
        WEIGHTS["business_impact"][factors.business_impact] * 0.6 +
        WEIGHTS["likelihood_of_exploit"][factors.likelihood_of_exploit] * 0.4
    )

    # Final CWSS formula
    cwss_score = base * attack_surface * environmental * 100.0
    return round(cwss_score, 2)
