import sys
sys.path.insert(0, "src")
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from quallki_agentic.feature_schema import FEATURE_NAMES
from quallki_agentic.qml_stub import infer_with_metadata

df = pd.read_csv("MasterDatasetProcessed_Clean.csv")

# Search broadly across attack types for ANY agreement
targets = ["Hulk", "SlowLoris", "Nmap", "Discov", "NosyN", "Alice2", "DevEva", "SuperSpy", "BaseLine"]

found = []
for attack_type in targets:
    rows = df[df["attack_type"] == attack_type]
    if len(rows) == 0:
        continue
    for i in range(min(50, len(rows))):
        row = rows.iloc[i]
        features = {feat: float(row[feat]) for feat in FEATURE_NAMES if feat in row}
        payload = {"message": f"{attack_type}", "source_ip": "10.0.0.1", "features": features}
        result = infer_with_metadata(payload)
        qml = result.get("label", "?")
        classical = result.get("classical_label", "?")
        if qml == classical:
            found.append((attack_type, i, qml, classical, rows.index[i]))
            print(f"AGREEMENT: true_type={attack_type}, row={i}, QML={qml}, Classical={classical}, df_idx={rows.index[i]}")
            break

if not found:
    print("\nNo agreement found. Showing distribution of classical predictions by true type:")
    for attack_type in targets:
        rows = df[df["attack_type"] == attack_type]
        if len(rows) == 0:
            continue
        row = rows.iloc[0]
        features = {feat: float(row[feat]) for feat in FEATURE_NAMES if feat in row}
        payload = {"message": f"{attack_type}", "source_ip": "10.0.0.1", "features": features}
        result = infer_with_metadata(payload)
        print(f"  {attack_type:12s}: QML={result.get('label'):15s} Classical={result.get('classical_label')}")
