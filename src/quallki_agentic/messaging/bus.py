from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from quallki_agentic.config import Settings


class MessageBus(Protocol):
    def publish(self, topic: str, event: dict[str, object]) -> None:
        ...


@dataclass
class InMemoryBus:
    events: deque[dict[str, object]] = field(default_factory=deque)

    def publish(self, topic: str, event: dict[str, object]) -> None:
        payload = {
            "topic": topic,
            "event": event,
            "published_at": datetime.now(UTC).isoformat(),
        }
        self.events.append(payload)


@dataclass
class RedisStreamBus:
    redis_url: str
    stream_name: str

    def __post_init__(self) -> None:
        import redis

        self._client = redis.Redis.from_url(self.redis_url, decode_responses=True)

    def publish(self, topic: str, event: dict[str, object]) -> None:
        payload = {
            "topic": topic,
            "event": json.dumps(event),
            "published_at": datetime.now(UTC).isoformat(),
        }
        self._client.xadd(self.stream_name, payload)


def build_message_bus(settings: Settings) -> MessageBus:
    backend = settings.message_bus_backend.strip().lower()
    if backend == "redis":
        try:
            return RedisStreamBus(
                redis_url=settings.redis_url,
                stream_name=settings.redis_stream_name,
            )
        except Exception:
            return InMemoryBus()
    return InMemoryBus()
