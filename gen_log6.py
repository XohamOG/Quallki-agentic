import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "src")
import pandas as pd, json
from quallki_agentic.feature_schema import FEATURE_NAMES

df = pd.read_csv("MasterDatasetProcessed_Clean.csv")
row = df[df["attack_type"] == "SlowLoris"].iloc[0]
features = {feat: float(row[feat]) for feat in FEATURE_NAMES if feat in row}

log6 = {
    "alert_id": "REAL-SLOWLORIS-DOS-006",
    "message": "Slow HTTP DoS attack detected against clinical web portal — partial connections keeping sockets open indefinitely.",
    "event_time": "2026-08-21T01:00:00Z",
    "source_ip": "198.51.100.55",
    "asset_type": "web_server",
    "clinical_impact": "high",
    "contains_phi": False,
    "logs": [
        "2026-08-21T01:00:00Z sensor=WAF rule=SlowHTTP_Connection src_ip=198.51.100.55 connections=480 state=HALF_OPEN",
        "2026-08-21T01:00:03Z host=WEB-PORTAL-01 source=Wazuh rule=31151 severity=10 description='Possible SlowLoris DoS: max worker threads exhausted'",
        "2026-08-21T01:00:05Z sensor=netflow src_ip=198.51.100.55 dst_port=443 bytes=9800 pkts=98 duration=45s flags=incomplete",
        "2026-08-21T01:00:08Z host=WEB-PORTAL-01 source=nginx error='upstream timed out (110: Connection timed out)' client=198.51.100.55",
        "2026-08-21T01:00:10Z host=WEB-PORTAL-01 source=Sysmon event_id=3 image=nginx protocol=tcp connections=480 state=ESTABLISHED"
    ],
    "features": features,
    "telemetry_signals": {
        "signal_strength": 0.85
    },
    "compliance_context": {
        "hipaa_applicable": True,
        "iso_scope": True,
        "gdpr_applicable": False,
        "soc2_scope": False,
        "nis2_applicable": False
    },
    "compliance_evidence": {
        "HIPAA-164.308(a)(6)": {
            "incident_ticket": "INC-2026-1099",
            "timeline": "SlowLoris DoS started at 01:00:00 UTC, WAF blocked at 01:02:30 UTC",
            "containment_record": "Source IP 198.51.100.55 null-routed at 01:02:30 UTC, nginx worker pool restarted",
            "outcome_record": "Portal restored at 01:04:00 UTC. No PHI exposure. Availability impact: 4 minutes.",
            "ticket_id": "INC-2026-1099",
            "approver": "SOC Tier 2 Lead",
            "execution_time": "2026-08-21T01:02:30Z",
            "source_system": "Wazuh + WAF",
            "integrity_hash": "sha256:c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
        },
        "NIST-CSF-2.0-RS.MA": {
            "incident_ticket": "INC-2026-1099",
            "triage_record": "P1 triage: high clinical impact, web portal unavailable, DoS confirmed by WAF signature",
            "response_record": "IP blocked, nginx restarted, upstream rate-limiting rules deployed",
            "ticket_id": "INC-2026-1099",
            "approver": "SOC Manager",
            "execution_time": "2026-08-21T01:02:30Z",
            "source_system": "ITSM"
        },
        "HIPAA-164.308(a)(1)": {
            "risk_analysis": "Annual risk assessment completed 2026-03-15 — DoS risk rated Medium",
            "risk_treatment": "WAF and rate-limiting controls deployed per risk treatment plan v3.1",
            "source_system": "GRC Platform",
            "event_time": "2026-08-21T01:00:00Z"
        },
        "ISO-27001-INCIDENT": {
            "isms_scope": "Clinical web portal and patient-facing services per ISMS v4.2",
            "incident_record": "INC-2026-1099 classified as P1 Availability incident — DoS",
            "corrective_action": "Rate-limiting, IP reputation filtering, nginx tuning, WAF rule update",
            "internal_audit": "Last internal audit 2026-06-01 — WAF coverage reviewed",
            "management_review": "DoS resilience review added to 2026-Q3 management agenda",
            "policy_approved": True,
            "owner_assigned": "ISMS Manager",
            "last_reviewed": "2026-06-01",
            "auditor_reference": "EXT-AUDIT-2026-Q2"
        }
    }
}

with open("log6.json", "w") as f:
    json.dump(log6, f, indent=2)

print("Written log6.json")
print(f"Features count: {len(features)}")
