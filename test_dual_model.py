import sys
sys.path.insert(0, "src")

from quallki_agentic.qml_stub import infer_with_metadata

# Quick test payload with realistic features - just use a few from the NMAP sample
payload = {
    "alert_id": "TEST-001",
    "message": "Network scan detected",
    "source_ip": "192.168.1.105",
    "features": {
        "flow_duration": 100.0,
        "flow_byts_s": 500.0,
        "tot_fwd_pkts": 10.0,
        "tot_bwd_pkts": 5.0,
        "syn_flag_cnt": 50.0,
        "proto_tcp": 1.0,
    }
}

result = infer_with_metadata(payload)
print("QML Label:      ", result.get("label", "N/A"))
print("QML Backend:    ", result.get("backend", "N/A"))
print("Classical Label:", result.get("classical_label", "N/A"))
print()

if result.get("classical_label", "unknown") != "unknown":
    print("[PASS] Classical model successfully ran alongside QML")
else:
    print("[WARN] Classical model returned unknown (check joblib path)")

if result.get("backend") == "qml_vqc":
    print("[PASS] QML VQC is active (no heuristic stub!)")
else:
    print("[WARN] QML is not using qml_vqc backend")
