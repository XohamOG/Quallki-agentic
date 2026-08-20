from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from quallki_agentic.feature_schema import FEATURE_NAMES


class QMLPreprocessor:
    """Reproduce the documented training-only QML preprocessing contract."""

    def __init__(self, artifact_path: str) -> None:
        path = Path(artifact_path)
        if not path.is_absolute() and not path.exists():
            path = Path(__file__).resolve().parents[2] / path
        self.path = path
        if not path.is_file():
            raise FileNotFoundError(
                f"QML preprocessing artifact not found: {path}. "
                "Create it from training data before raw-feature inference."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        self.log_features = tuple(str(name) for name in data["log_features"])
        self.mean = self._vector(data["mean"], "mean")
        self.scale = self._vector(data["scale"], "scale")
        self.latent_min = self._latent_vector(data["latent_min"], "latent_min")
        self.latent_max = self._latent_vector(data["latent_max"], "latent_max")
        if any(name not in FEATURE_NAMES for name in self.log_features):
            raise ValueError("log_features contains an unknown feature name")
        if np.any(self.scale <= 0):
            raise ValueError("scale values must be greater than zero")
        if np.any(self.latent_max <= self.latent_min):
            raise ValueError("latent_max values must exceed latent_min values")

    @staticmethod
    def _vector(values: Any, name: str) -> np.ndarray:
        vector = np.asarray(values, dtype=np.float32)
        if vector.shape != (len(FEATURE_NAMES),):
            raise ValueError(f"{name} must contain {len(FEATURE_NAMES)} values")
        return vector

    @staticmethod
    def _latent_vector(values: Any, name: str) -> np.ndarray:
        vector = np.asarray(values, dtype=np.float32)
        if vector.shape != (6,):
            raise ValueError(f"{name} must contain 6 values")
        return vector

    def transform(self, values: list[float]) -> np.ndarray:
        vector = np.asarray(values, dtype=np.float32)
        if vector.shape != (len(FEATURE_NAMES),):
            raise ValueError(f"Expected {len(FEATURE_NAMES)} features")
        transformed = vector.copy()
        for feature in self.log_features:
            index = FEATURE_NAMES.index(feature)
            transformed[index] = np.log1p(max(0.0, float(transformed[index])))
        return (transformed - self.mean) / self.scale

    def scale_latent_to_pi(self, latent: np.ndarray) -> np.ndarray:
        values = np.asarray(latent, dtype=np.float32).reshape(6)
        denominator = self.latent_max - self.latent_min
        scaled = 2 * np.pi * ((values - self.latent_min) / denominator) - np.pi
        return np.clip(scaled, -np.pi, np.pi).astype(np.float32)

    @staticmethod
    def example_artifact() -> dict[str, Any]:
        """Return the schema shape without fake training statistics."""
        return {
            "log_features": [],
            "mean": [0.0] * len(FEATURE_NAMES),
            "scale": [1.0] * len(FEATURE_NAMES),
            "latent_min": [-1.0] * 6,
            "latent_max": [1.0] * 6,
        }
