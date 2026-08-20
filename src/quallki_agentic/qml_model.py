from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from quallki_agentic.config import Settings
from quallki_agentic.feature_schema import build_feature_vector

MODEL_LABELS = (
    "BaseLine", "Alice2", "DevEva", "Discov", "Hulk",
    "Nmap", "NosyN", "Ransac", "SlowLoris", "SuperSpy",
)


def _six_inputs(payload: dict[str, Any], encoder: Any = None) -> np.ndarray:
    raw = payload.get("qml_input")
    if isinstance(raw, (list, tuple)):
        if len(raw) != 6:
            raise ValueError("qml_input must contain exactly 6 values")
        return np.asarray(raw, dtype=np.float32)

    values, _ = build_feature_vector(payload)
    if encoder is None:
        raise RuntimeError("The 99-to-6 autoencoder is required for QML inference")
    import torch

    with torch.inference_mode():
        encoded = encoder(torch.from_numpy(np.asarray(values, dtype=np.float32)).reshape(1, -1))
    return encoded.detach().cpu().numpy().reshape(6).astype(np.float32)


class QMLVQCClassifier:
    """Adapter for the supplied 6-qubit VQC checkpoint.

    The checkpoint stores a StronglyEntanglingLayers tensor with shape
    ``(4, 6, 3)`` and a ten-class linear head. Since preprocessing metadata is
    not included, real callers can provide six preprocessed values as
    ``qml_input``; otherwise this adapter uses the documented 99-to-6 group
    reduction in ``_six_inputs``.
    """

    def __init__(self, model_path: str, autoencoder_path: str) -> None:
        self.model_path = model_path
        self.autoencoder_path = autoencoder_path
        self._model: Any = None
        self._encoder: Any = None
        self.load_error: str | None = None
        try:
            self._encoder = self._load_autoencoder(autoencoder_path)
            self._model = self._load(model_path)
        except Exception as exc:
            self.load_error = f"{type(exc).__name__}: {exc}"

    @property
    def available(self) -> bool:
        return self._model is not None

    def _load(self, model_path: str) -> Any:
        import pennylane as qml
        import torch
        from torch import nn

        path = self._resolve_path(model_path)

        wires = list(range(6))
        dev = qml.device("default.qubit", wires=6)

        @qml.qnode(dev, interface="torch")
        def circuit(inputs: Any, weights: Any) -> Any:
            qml.AngleEmbedding(inputs, wires=wires, rotation="Y")
            qml.StronglyEntanglingLayers(weights, wires=wires)
            return [qml.expval(qml.PauliZ(wire)) for wire in wires]

        qnn = qml.qnn.TorchLayer(circuit, {"weights": (4, 6, 3)})

        class VQCClassifier(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.qnn = qnn
                self.linear = nn.Linear(6, 10)

            def forward(self, inputs: Any) -> Any:
                return self.linear(self.qnn(inputs))

        model = VQCClassifier()
        state = self._read_state(path, torch)
        model.load_state_dict(state, strict=True)
        model.eval()
        return model

    @staticmethod
    def _resolve_path(model_path: str) -> Path:
        path = Path(model_path)
        if not path.is_absolute() and not path.exists():
            path = Path(__file__).resolve().parents[2] / path
        return path

    def _load_autoencoder(self, model_path: str) -> Any:
        import torch
        from torch import nn

        class Encoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(99, 64),
                    nn.ReLU(),
                    nn.Linear(64, 6),
                )

            def forward(self, inputs: Any) -> Any:
                return self.encoder(inputs)

        encoder = Encoder()
        state = self._read_state(self._resolve_path(model_path), torch, prefix="encoder.")
        encoder.encoder.load_state_dict(state, strict=True)
        encoder.eval()
        return encoder.encoder

    @staticmethod
    def _read_state(path: Path, torch: Any, prefix: str = "") -> dict[str, Any]:
        archive_root = path
        if path.is_dir() and not (path / "data").is_dir():
            candidates = list(path.rglob("data/0"))
            if candidates:
                archive_root = candidates[0].parent.parent
        if archive_root.is_file():
            loaded = torch.load(archive_root, map_location="cpu", weights_only=True)
            if not isinstance(loaded, dict):
                raise TypeError("QML checkpoint must contain a state dictionary")
            return {
                key.removeprefix(prefix): value
                for key, value in loaded.items()
                if key.startswith(prefix)
            }

        data_dir = archive_root / "data"
        if not data_dir.is_dir():
            raise FileNotFoundError(f"No Torch checkpoint data directory under {archive_root}")
        if prefix == "encoder.":
            return {
                "0.weight": torch.from_numpy(np.fromfile(data_dir / "0", dtype=np.float32).reshape(64, 99)),
                "0.bias": torch.from_numpy(np.fromfile(data_dir / "1", dtype=np.float32).reshape(64)),
                "2.weight": torch.from_numpy(np.fromfile(data_dir / "2", dtype=np.float32).reshape(6, 64)),
                "2.bias": torch.from_numpy(np.fromfile(data_dir / "3", dtype=np.float32).reshape(6)),
            }
        return {
            "qnn.weights": torch.from_numpy(np.fromfile(data_dir / "0", dtype=np.float32).reshape(4, 6, 3)),
            "linear.weight": torch.from_numpy(np.fromfile(data_dir / "1", dtype=np.float32).reshape(10, 6)),
            "linear.bias": torch.from_numpy(np.fromfile(data_dir / "2", dtype=np.float32).reshape(10)),
        }

    def predict_label(self, payload: dict[str, Any]) -> str:
        if not self.available:
            raise RuntimeError(self.load_error or "QML model is unavailable")
        import torch

        inputs = torch.from_numpy(_six_inputs(payload, self._encoder)).reshape(1, 6)
        with torch.inference_mode():
            logits = self._model(inputs)
        return MODEL_LABELS[int(torch.argmax(logits, dim=1).item())]


def canonical_label(label: str) -> str:
    normalized = label.strip().lower()
    return {
        "baseline": "normal",
        "discov": "recon",
        "nmap": "recon",
        "hulk": "dos",
        "slowloris": "dos",
        "ransac": "ransomware",
    }.get(normalized, normalized)
