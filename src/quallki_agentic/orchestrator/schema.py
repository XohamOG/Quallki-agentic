from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class AlertObject:
    alert_id: str
    source_ip: str
    event_time: str
    message: str
    qml_label: str
    iocs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TriageResult:
    priority: str
    confidence: float
    reasoning: str
    auto_close: bool


@dataclass(frozen=True)
class ThreatIntelResult:
    attack_techniques: list[str]
    related_campaigns: list[str]
    cve_links: list[str]


@dataclass(frozen=True)
class AgentResponse:
    agent_name: str
    status: str
    summary: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class TaskAssignment:
    task_id: str
    target_agent: str
    reason: str
    created_at: str


def now_iso() -> str:
    return datetime.now(UTC).isoformat()
