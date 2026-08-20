import json
import pandas as pd
from quallki_agentic.feature_schema import FEATURE_NAMES

def generate_logs():
    print("Loading dataset...")
    df = pd.read_csv("MasterDatasetProcessed_Clean.csv")
    
    # Get rows
    baseline_rows = df[df["attack_type"] == "BaseLine"]
    alice2_rows = df[df["attack_type"] == "Alice2"]
    nmap_rows = df[df["attack_type"] == "Nmap"]
    ransac_rows = df[df["attack_type"] == "Ransac"]
    
    output = []
    
    if len(baseline_rows) > 0:
        baseline = baseline_rows.iloc[0]
        b_features = {feat: float(baseline[feat]) for feat in FEATURE_NAMES if feat in baseline}
        b_alert = {
            "alert_id": "REAL-BASE-001",
            "message": "Routine background health check and backup activity.",
            "event_time": "2026-08-21T00:00:00Z",
            "source_ip": "10.0.50.12",
            "asset_type": "backup_server",
            "clinical_impact": "low",
            "contains_phi": False,
            "logs": [
                "2026-08-21T00:00:00Z host=BACKUP-01 source=Sysmon event_id=3 image=backup_agent.exe protocol=tcp src_ip=10.0.50.12 dst_port=443",
                f"2026-08-21T00:00:10Z sensor=netflow bytes={int(b_features.get('fwd_byts_b_avg', 0))} pkts={int(b_features.get('tot_fwd_pkts', 0))}"
            ],
            "features": b_features,
            "telemetry_signals": {"signal_strength": 0.1}
        }
        output.append(b_alert)
    
    if len(alice2_rows) > 0:
        attack = alice2_rows.iloc[0]
        a_features = {feat: float(attack[feat]) for feat in FEATURE_NAMES if feat in attack}
        a_alert = {
            "alert_id": "REAL-ALICE2-002",
            "message": "Intense network scanning or data exfiltration detected.",
            "event_time": "2026-08-21T00:05:00Z",
            "source_ip": "198.51.100.99",
            "asset_type": "workstation",
            "clinical_impact": "high",
            "contains_phi": True,
            "logs": [
                "2026-08-21T00:05:00Z host=WKST-09 source=Wazuh rule=60001 severity=12 description='suspicious process injection'",
                f"2026-08-21T00:05:05Z sensor=netflow bytes={int(a_features.get('fwd_byts_b_avg', 0))} pkts={int(a_features.get('tot_fwd_pkts', 0))} action=allowed",
                "2026-08-21T00:05:08Z sensor=IDS signature=DATA_EXFILTRATION_ALICE2 endpoints=42"
            ],
            "features": a_features,
            "telemetry_signals": {"signal_strength": 0.95}
        }
        output.append(a_alert)
        
    if len(nmap_rows) > 0:
        nmap_atk = nmap_rows.iloc[0]
        n_features = {feat: float(nmap_atk[feat]) for feat in FEATURE_NAMES if feat in nmap_atk}
        n_alert = {
            "alert_id": "REAL-NMAP-003",
            "message": "Network reconnaissance and port scanning activity detected.",
            "event_time": "2026-08-21T00:10:00Z",
            "source_ip": "192.168.1.105",
            "asset_type": "web_server",
            "clinical_impact": "medium",
            "contains_phi": False,
            "logs": [
                "2026-08-21T00:10:00Z sensor=netflow tcp_flags=S pkts=100",
                "2026-08-21T00:10:02Z sensor=IDS signature=NMAP_SYN_SCAN endpoints=1"
            ],
            "features": n_features,
            "telemetry_signals": {"signal_strength": 0.8}
        }
        output.append(n_alert)

    if len(ransac_rows) > 0:
        ransac_atk = ransac_rows.iloc[0]
        r_features = {feat: float(ransac_atk[feat]) for feat in FEATURE_NAMES if feat in ransac_atk}
        r_alert = {
            "alert_id": "REAL-RANSOM-004",
            "message": "Ransomware encryption activity detected on file shares.",
            "event_time": "2026-08-21T00:15:00Z",
            "source_ip": "10.0.10.22",
            "asset_type": "ehr_server",
            "clinical_impact": "critical",
            "contains_phi": True,
            "logs": [
                "2026-08-21T00:15:00Z host=EHR-DB source=Wazuh rule=9999 severity=15 description='Mass file encryption detected'",
                "2026-08-21T00:15:02Z host=EHR-DB event_id=4624 user=admin logon_type=3",
                "2026-08-21T00:15:05Z sensor=netflow payload_bytes=1000000"
            ],
            "features": r_features,
            "telemetry_signals": {"signal_strength": 0.99}
        }
        output.append(r_alert)
    
    with open("logs-only-realistic.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("Generated logs-only-realistic.json successfully.")

if __name__ == "__main__":
    generate_logs()
