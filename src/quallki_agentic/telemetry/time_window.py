from __future__ import annotations

from datetime import UTC, datetime, timedelta


def make_time_window(seconds: int = 1) -> dict[str, str]:
    end = datetime.now(UTC)
    start = end - timedelta(seconds=seconds)
    return {"start": start.isoformat(), "end": end.isoformat(), "size_seconds": str(seconds)}
