from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from quallki_agentic.config import Settings


@dataclass
class QuantumEnsembleClient:
    """Bridge for current classical model and future QML model integration."""

    endpoint: str = "http://localhost:8001/infer"

    def __post_init__(self) -> None:
        self._settings = Settings.from_env()
        self._model = None
        self._label_list = [item.strip() for item in self._settings.model_label_list.split(",") if item.strip()]

        model_path = Path(self._settings.classical_model_path)
        if model_path.exists():
            try:
                import joblib

                self._model = joblib.load(model_path)
            except Exception:
                self._model = None

    def _predict_from_classical_model(self, message: str) -> tuple[str, float] | None:
        if self._model is None:
            return None

        n_features = int(getattr(self._model, "n_features_in_", 0))
        if n_features <= 0:
            return None

        vector = np.zeros((1, n_features), dtype=float)

        lowered = message.lower()
        signal_tokens = [
            "ransomware",
            "encrypt",
            "dos",
            "ddos",
            "scan",
            "recon",
            "credential",
            "failed login",
            "cve-",
        ]
        token_hits = sum(1 for token in signal_tokens if token in lowered)
        vector[0, 0] = float(len(message))
        if n_features > 1:
            vector[0, 1] = float(token_hits)
        if n_features > 2:
            vector[0, 2] = 1.0 if "cve-" in lowered else 0.0

        try:
            probs = self._model.predict_proba(vector)
            top_index = int(np.argmax(probs[0]))
            confidence = float(probs[0][top_index])
            label = str(top_index)
            if top_index < len(self._label_list):
                label = self._label_list[top_index]
            return (label.lower(), confidence)
        except Exception:
            return None

    def infer_label(self, message: str) -> tuple[str, float]:
        predicted = self._predict_from_classical_model(message)
        if predicted is not None:
            return predicted

        lowered = message.lower()
        if any(token in lowered for token in ["ransomware", "encrypt", "malware"]):
            return ("malware", 0.84)
        if any(token in lowered for token in ["ddos", "dos", "flood"]):
            return ("dos", 0.8)
        if any(token in lowered for token in ["bruteforce", "credential", "failed login"]):
            return ("brute_force", 0.76)
        if any(token in lowered for token in ["scan", "recon", "probe"]):
            return ("recon", 0.71)
        return ("normal", 0.62)
