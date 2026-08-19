from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BB84Result:
    shared_key: str
    qber: float
    eve_detected: bool


def simulate_bb84(n_bits: int = 128, under_attack: bool = False) -> BB84Result:
    base_error = 0.02
    attack_error = 0.28 if under_attack else 0.0
    qber = base_error + attack_error + random.uniform(0, 0.02)
    eve_detected = qber > 0.25
    key_size = max(16, n_bits // 2)
    key = "".join(random.choice("01") for _ in range(key_size))
    return BB84Result(shared_key=key, qber=qber, eve_detected=eve_detected)
