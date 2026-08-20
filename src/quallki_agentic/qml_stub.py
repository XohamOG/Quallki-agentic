from __future__ import annotations

from typing import Any


def infer(payload: dict[str, Any]) -> dict[str, str]:
    """Return only a QML attack category label for the current demo stub."""
    qml_label = payload.get("qml_label")
    if qml_label:
        return {"label": str(qml_label)}

    message = str(payload.get("message", "")).lower()
    if "ransom" in message or "encrypt" in message:
        return {"label": "ransomware"}
    if "sql" in message or "select " in message:
        return {"label": "sql-injection"}
    if "credential" in message or "login failed" in message or "failed login" in message:
        return {"label": "credential-theft"}
    if "scan" in message or "recon" in message or "probe" in message:
        return {"label": "recon"}
    return {"label": "unknown"}