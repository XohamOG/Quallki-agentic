import warnings
from typing import Any
import numpy as np

# Suppress sklearn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from quallki_agentic.feature_schema import build_feature_vector

MODEL_LABELS = (
    "BaseLine", "Alice2", "DevEva", "Discov", "Hulk",
    "Nmap", "NosyN", "Ransac", "SlowLoris", "SuperSpy",
)

class ClassicalClassifier:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self._model = None
        self.load_error: str | None = None
        try:
            import joblib
            self._model = joblib.load(model_path)
        except Exception as exc:
            self.load_error = f"{type(exc).__name__}: {exc}"

    @property
    def available(self) -> bool:
        return self._model is not None

    def predict_label(self, payload: dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError(self.load_error or "Classical model is unavailable")
            
        values, _ = build_feature_vector(payload)
        features_array = np.array([values], dtype=np.float32)
        
        try:
            pred_idx = self._model.predict(features_array)[0]
            # In case it predicts a string label directly:
            if isinstance(pred_idx, str):
                return pred_idx
            return MODEL_LABELS[int(pred_idx)]
        except Exception as e:
            return "unknown"
