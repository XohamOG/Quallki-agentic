from __future__ import annotations

from dataclasses import dataclass, field

from quallki_agentic.crypto.qkd_bb84 import simulate_bb84


@dataclass
class QKDKeyManager:
    pool: dict[str, list[str]] = field(default_factory=dict)

    def rotate(self, agent_pair: str) -> dict[str, object]:
        result = simulate_bb84()
        self.pool.setdefault(agent_pair, []).append(result.shared_key)
        return {
            "agent_pair": agent_pair,
            "qber": result.qber,
            "eve_detected": result.eve_detected,
            "pool_size": len(self.pool[agent_pair]),
        }

    def pop_key(self, agent_pair: str) -> str | None:
        keys = self.pool.get(agent_pair, [])
        if not keys:
            return None
        return keys.pop(0)
