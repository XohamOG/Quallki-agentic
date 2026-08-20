from typing import Any


def build_orchestrator_graph(*args: Any, **kwargs: Any) -> Any:
	from quallki_agentic.orchestrator.graph import build_orchestrator_graph as _build

	return _build(*args, **kwargs)

__all__ = ["build_orchestrator_graph"]
