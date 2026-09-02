from __future__ import annotations

ATTACK_TO_CWE_MAP = {
    # Network Service Scanning / Port Scanning
    "T1046": [
        {"cwe_id": "CWE-200", "name": "Exposure of Sensitive Information to an Unauthorized Actor", "capec": "CAPEC-118"},
    ],
    # Exploit Public-Facing Application (SQL Injection)
    "T1190": [
        {"cwe_id": "CWE-89", "name": "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')", "capec": "CAPEC-66"},
        {"cwe_id": "CWE-20", "name": "Improper Input Validation", "capec": "CAPEC-153"},
        {"cwe_id": "CWE-94", "name": "Improper Control of Generation of Code ('Code Injection')", "capec": "CAPEC-242"}
    ],
    # Process Injection
    "T1055": [
        {"cwe_id": "CWE-250", "name": "Execution with Unnecessary Privileges", "capec": "CAPEC-640"},
        {"cwe_id": "CWE-119", "name": "Improper Restriction of Operations within the Bounds of a Memory Buffer", "capec": "CAPEC-100"}
    ],
    # Sudo / Privilege Escalation
    "T1548.003": [
        {"cwe_id": "CWE-269", "name": "Improper Privilege Management", "capec": "CAPEC-233"},
        {"cwe_id": "CWE-250", "name": "Execution with Unnecessary Privileges", "capec": "CAPEC-17"}
    ],
    # Credential Stuffing
    "T1110.004": [
        {"cwe_id": "CWE-307", "name": "Improper Restriction of Excessive Authentication Attempts", "capec": "CAPEC-70"},
        {"cwe_id": "CWE-799", "name": "Improper Control of Interaction Frequency", "capec": "CAPEC-565"}
    ],
    # Pass-the-Hash / Lateral Movement
    "T1550.002": [
        {"cwe_id": "CWE-287", "name": "Improper Authentication", "capec": "CAPEC-645"},
        {"cwe_id": "CWE-294", "name": "Authentication Bypass by Capture-replay", "capec": "CAPEC-601"}
    ],
    # Heartbleed TLS Memory Leak
    "T1212": [
        {"cwe_id": "CWE-126", "name": "Buffer Over-read", "capec": "CAPEC-540"},
        {"cwe_id": "CWE-200", "name": "Exposure of Sensitive Information to an Unauthorized Actor", "capec": "CAPEC-118"}
    ],
    # Ransomware / Data Encrypted for Impact
    "T1486": [
        {"cwe_id": "CWE-732", "name": "Incorrect Permission Assignment for Critical Resource", "capec": "CAPEC-17"}
    ],
    # Endpoint Denial of Service
    "T1499": [
        {"cwe_id": "CWE-400", "name": "Uncontrolled Resource Consumption", "capec": "CAPEC-119"}
    ]
}
