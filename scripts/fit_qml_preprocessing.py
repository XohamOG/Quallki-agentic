from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from quallki_agentic.feature_schema import FEATURE_NAMES
from quallki_agentic.qml_model import QMLVQCClassifier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fit training-only QML preprocessing statistics from the cleaned feature CSV."
    )
    parser.add_argument("--csv", type=Path, required=True, help="Training-only cleaned CSV")
    parser.add_argument("--autoencoder", type=Path, default=Path("best_qml_autoencoder_6q.pt"))
    parser.add_argument("--output", type=Path, default=Path("qml_preprocessing.json"))
    parser.add_argument(
        "--log-features",
        required=True,
        help="Exact 19 training log-feature names, comma-separated",
    )
    return parser.parse_args()


def load_encoder(path: Path) -> nn.Module:
    class Encoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = nn.Sequential(nn.Linear(99, 64), nn.ReLU(), nn.Linear(64, 6))

        def forward(self, inputs: torch.Tensor) -> torch.Tensor:
            return self.encoder(inputs)

    encoder = Encoder()
    state = QMLVQCClassifier._read_state(path, torch, prefix="encoder.")
    encoder.encoder.load_state_dict(state, strict=True)
    encoder.eval()
    return encoder.encoder


def main() -> None:
    args = parse_args()
    log_features = [name.strip() for name in args.log_features.split(",") if name.strip()]
    unknown = sorted(set(log_features) - set(FEATURE_NAMES))
    if unknown or len(log_features) != 19:
        raise SystemExit(f"--log-features must contain the exact 19 known names; invalid={unknown}")

    frame = pd.read_csv(args.csv, usecols=list(FEATURE_NAMES))
    values = frame.to_numpy(dtype=np.float32)
    for name in log_features:
        index = FEATURE_NAMES.index(name)
        values[:, index] = np.log1p(np.maximum(values[:, index], 0.0))

    mean = values.mean(axis=0)
    scale = values.std(axis=0)
    scale[scale == 0] = 1.0
    standardized = (values - mean) / scale

    encoder = load_encoder(args.autoencoder)
    with torch.inference_mode():
        latent = encoder(torch.from_numpy(standardized)).numpy()
    latent_min = latent.min(axis=0)
    latent_max = latent.max(axis=0)

    artifact = {
        "feature_names": list(FEATURE_NAMES),
        "log_features": log_features,
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "latent_min": latent_min.tolist(),
        "latent_max": latent_max.tolist(),
        "fit_rows": int(len(frame)),
        "fit_source": str(args.csv),
        "warning": "Statistics must be fit on training data only and versioned with the model.",
    }
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} using {len(frame)} training rows")


if __name__ == "__main__":
    main()
