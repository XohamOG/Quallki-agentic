from __future__ import annotations

import argparse

from dotenv import load_dotenv

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.healthcare.demo_runner import run_healthcare_demo_scenario


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quallki agentic SOC triage runner")
    parser.add_argument(
        "--scenario",
        default="ehr_ransomware",
        choices=sorted(HOSPITAL_DEMO_CASES.keys()),
        help="Healthcare demo scenario key",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv()
    run_data = run_healthcare_demo_scenario(args.scenario)
    scenario = run_data["scenario"]
    label = run_data["label"]
    confidence = run_data["confidence"]
    result = run_data["result"]

    print("\n=== TRIAGE RESULT ===")
    print(f"Scenario: {args.scenario} - {scenario['title']}")
    print(f"Label: {label}")
    print(f"QML backend: {run_data.get('qml_backend', 'unknown')}")
    print(f"Confidence: {confidence:.2f}")

    print("\nSimulated Logs:")
    for log in run_data.get("logs", []):
        print(f"- {log}")

    alert = result.get("alert_object", {})
    if isinstance(alert, dict):
        analysis = alert.get("analysis", {})
        print("\nDetection Analysis:")
        print(f"Attack vector: {analysis.get('attack_vector', 'unknown')}")
        print(f"IOCs: {', '.join(analysis.get('iocs', [])) or 'none'}")
        print(f"Likely CWEs: {', '.join(analysis.get('likely_cwes', [])) or 'none'}")
        print(f"CWSS-like score: {alert.get('cwss', {}).get('score', 0.0)}")

    triage = result.get("triage_result", {})
    if isinstance(triage, dict):
        print(f"Priority: {triage.get('priority', 'P4')}")
        print(f"Triage Reasoning: {triage.get('reasoning', 'n/a')}")

    actions = result.get("recommended_actions", [])
    if actions:
        print("\nRecommended Actions:")
        for index, action in enumerate(actions, start=1):
            print(f"{index}. {action}")

    response_actions = result.get("response_actions", [])
    if response_actions:
        print("\nContainment Actions:")
        for index, action in enumerate(response_actions, start=1):
            print(f"{index}. {action}")

    checklist = result.get("compliance_checklist", [])
    compliance_assessment = result.get("compliance_assessment", {})
    if isinstance(checklist, list) and checklist:
        print("\nCompliance Evidence Mapping:")
        if isinstance(compliance_assessment, dict):
            print(f"Assessment metrics: {compliance_assessment}")
        for item in checklist:
            if isinstance(item, dict):
                print(
                    f"- {item.get('id', '?')} [{item.get('status', 'not_evidenced')}] "
                    f"{item.get('framework', '')} | {item.get('control', '')} | "
                    f"Owner: {item.get('owner', 'unassigned')}"
                )

    print("\nSOC Summary:")
    print(result.get("final_summary", "No summary generated."))


if __name__ == "__main__":
    main()
