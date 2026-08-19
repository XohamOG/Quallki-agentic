from __future__ import annotations

from dataclasses import dataclass

from quallki_agentic.telemetry.time_window import make_time_window


@dataclass
class TelemetryIngestion:
    source: str = "wazuh"

    def ingest_alert(self, message: str, source_ip: str = "10.0.0.5") -> dict[str, object]:
        return {
            "message": message,
            "source_ip": source_ip,
            "window": make_time_window(seconds=1),
            "source": self.source,
        }
