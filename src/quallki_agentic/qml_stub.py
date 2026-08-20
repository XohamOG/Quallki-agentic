from __future__ import annotations

from typing import Any

from quallki_agentic.config import Settings
from quallki_agentic.qml_model import QMLVQCClassifier, canonical_label


_classifier: QMLVQCClassifier | None = None
_classical: Any = None


def infer_with_metadata(payload: dict[str, Any]) -> dict[str, str]:
    global _classifier, _classical
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
    
    if _classical is None:
        try:
            from quallki_agentic.classical_model import ClassicalClassifier
            _classical = ClassicalClassifier("best_regularized_model.joblib")
        except Exception:
            _classical = None
            
    result = {}
    
    if _classifier and _classifier.available:
        result["label"] = canonical_label(_classifier.predict_label(payload))
        result["backend"] = "qml_vqc"
    else:
        result["label"] = _heuristic_label(payload)
        result["backend"] = "heuristic_stub"
        
    if _classical and _classical.available:
        result["classical_label"] = canonical_label(_classical.predict_label(payload))
    else:
        result["classical_label"] = "unknown"
        
    return result


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