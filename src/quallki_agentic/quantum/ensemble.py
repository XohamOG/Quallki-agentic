from __future__ import annotations

class QuantumEnsembleClient:
    """Compatibility adapter for the QML endpoint/stub."""

    def __init__(self, endpoint: str = "http://localhost:8001/infer") -> None:
        self.endpoint = endpoint

    def infer(self, payload: dict[str, object]) -> dict[str, str]:
        from quallki_agentic.qml_stub import infer

        return infer(payload)

    def infer_label(self, message: str) -> str:
        return self.infer({"message": message})["label"]
