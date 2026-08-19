from __future__ import annotations

from quallki_agentic.orchestrator.state import OrchestratorState


def route_after_triage(state: OrchestratorState) -> str:
    route = state.get("route", "auto_close")
    if route in {"response_path", "investigate_path", "auto_close"}:
        return route
    return "auto_close"
