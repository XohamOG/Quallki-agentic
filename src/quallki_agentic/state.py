from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class ClassificationResult:
    label: str
    severity: str
    confidence: float


class AgentState(TypedDict, total=False):
    message: str
    normalized_alert: str
    classification_label: str
    severity: str
    confidence: float
    context_snippets: list[str]
    recommended_actions: list[str]
    response: str
