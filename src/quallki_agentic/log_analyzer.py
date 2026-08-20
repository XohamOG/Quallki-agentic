from __future__ import annotations

import re
from typing import Any


_IOC_PATTERNS = (
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE),
    re.compile(r"\b[a-f0-9]{32,64}\b", re.IGNORECASE),
    re.compile(r"\b[a-z0-9.-]+\.(?:com|net|org|io|ru|cn)\b", re.IGNORECASE),
)


def analyze(payload: dict[str, Any], qml_label: str) -> dict[str, Any]:
    raw_logs = payload.get("logs", [])
    logs = [str(log) for log in raw_logs] if isinstance(raw_logs, list) else []
    message = "\n".join(
        [str(payload.get("message", "")), str(payload.get("source_ip", "")), *logs]
    )
    lowered = message.lower()
    iocs: list[str] = []
    for pattern in _IOC_PATTERNS:
        iocs.extend(pattern.findall(message))
    iocs = list(dict.fromkeys(iocs))

    evidence: list[str] = []
    attack_vector = "unknown"
    cwes: list[str] = []
    indicators = (
        ("ransomware", "encryption activity detected", "endpoint", "CWE-732"),
        ("encrypt", "file encryption indicator", "endpoint", "CWE-434"),
        ("sql", "SQL injection syntax observed", "web application", "CWE-89"),
        ("select ", "SQL query syntax observed", "web application", "CWE-89"),
        ("login failed", "repeated authentication failure", "identity", "CWE-307"),
        ("credential", "credential access indicator", "identity", "CWE-522"),
        ("powershell", "PowerShell execution observed", "command execution", "CWE-78"),
        ("scan", "network scanning indicator", "network", "CWE-200"),
        ("port", "port enumeration indicator", "network", "CWE-200"),
        ("exfil", "possible data exfiltration", "data transfer", "CWE-359"),
    )
    for token, statement, vector, cwe in indicators:
        if token in lowered:
            evidence.append(statement)
            attack_vector = vector
            if cwe not in cwes:
                cwes.append(cwe)

    label = qml_label.lower()
    label_cwe = {
        "ransomware": "CWE-732",
        "malware": "CWE-94",
        "credential-theft": "CWE-522",
        "brute_force": "CWE-307",
        "sql-injection": "CWE-89",
        "dos": "CWE-400",
        "recon": "CWE-200",
    }.get(label)
    if label_cwe and label_cwe not in cwes:
        cwes.append(label_cwe)
    if iocs:
        evidence.append(f"{len(iocs)} IOC(s) extracted from the event")

    affected = payload.get("affected_assets", payload.get("asset_type", "unknown"))
    if isinstance(affected, str):
        affected = [affected]
    elif not isinstance(affected, list):
        affected = [str(affected)]

    return {
        "attack_vector": attack_vector,
        "evidence": list(dict.fromkeys(evidence)),
        "iocs": iocs,
        "likely_cwes": cwes,
        "affected": [str(asset) for asset in affected],
    }