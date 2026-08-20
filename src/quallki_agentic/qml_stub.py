from __future__ import annotations

from typing import Any

from quallki_agentic.config import Settings
from quallki_agentic.qml_model import QMLVQCClassifier, canonical_label


_classifier: QMLVQCClassifier | None = None


def infer_with_metadata(payload: dict[str, Any]) -> dict[str, str]:
    global _classifier
    has_model_input = any(
        key in payload for key in ("feature_vector", "features", "qml_input", "logs")
    )
    qml_label = payload.get("qml_label")
    if qml_label and not has_model_input:
        return {"label": str(qml_label), "backend": "explicit_label"}
    if _classifier is None:
        settings = Settings.from_env()
        _classifier = QMLVQCClassifier(
            settings.qml_model_path,
            settings.qml_autoencoder_path,
            settings.qml_preprocessing_path,
        )
    if _classifier.available:
        return {
            "label": canonical_label(_classifier.predict_label(payload)),
            "backend": "qml_vqc",
        }

    return {"label": _heuristic_label(payload), "backend": "heuristic_stub"}


def _heuristic_label(payload: dict[str, Any]) -> str:
    message = str(payload.get("message", "")).lower()
    if "ransom" in message or "encrypt" in message:
        return "ransomware"
    if "sql" in message or "select " in message:
        return "sql-injection"
    if "credential" in message or "login failed" in message or "failed login" in message:
        return "credential-theft"
    if "scan" in message or "recon" in message or "probe" in message:
        return "recon"
    return "unknown"


def infer(payload: dict[str, Any]) -> dict[str, str]:
    """Return only a QML attack category label for the current demo stub."""
    return {"label": infer_with_metadata(payload)["label"]}