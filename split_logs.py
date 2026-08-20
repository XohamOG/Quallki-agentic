import json

with open("logs-only-realistic.json") as f:
    alerts = json.load(f)

for i, alert in enumerate(alerts, 1):
    fname = f"log{i}.json"
    with open(fname, "w") as out:
        json.dump(alert, out, indent=2)
    print(f"Wrote {fname} -> alert_id={alert['alert_id']}")

print(f"Done. Split {len(alerts)} alerts into {len(alerts)} files.")
