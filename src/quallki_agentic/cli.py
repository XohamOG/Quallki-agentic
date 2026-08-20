from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.healthcare.demo_runner import run_alert_payload, run_healthcare_demo_scenario


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quallki agentic SOC triage runner")
    parser.add_argument(
        "--scenario",
        choices=sorted(HOSPITAL_DEMO_CASES.keys()),
        help="Run a built-in synthetic healthcare scenario",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Run a real normalized alert from a JSON file or JSONL file",
    )
    return parser.parse_args()


def _load_input(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Input file is empty")
    try:
        parsed = json.loads(text)
        records = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("Each input record must be a JSON object")
    return records


def main() -> None:
    args = parse_args()
    load_dotenv()
    if bool(args.scenario) == bool(args.input):
        raise SystemExit("Choose exactly one of --scenario or --input")
    run_data_list = (
        [run_healthcare_demo_scenario(args.scenario)]
        if args.scenario
        else [run_alert_payload(record) for record in _load_input(args.input)]
    )
    for run_data in run_data_list:
        _print_run(run_data)


def _print_run(run_data: dict[str, object]) -> None:
    scenario = run_data["scenario"]
    label = run_data["label"]
    confidence = run_data["confidence"]
    result = run_data["result"]

    print("\n=== TRIAGE RESULT ===")
    print(f"Scenario: {run_data['scenario_key']} - {scenario['title']}")
    print(f"Label: {label}")
    print(f"QML backend: {run_data.get('qml_backend', 'unknown')}")
    trace = run_data.get("workflow_trace", [])
    if isinstance(trace, list):
        nodes = [str(item.get("node")) for item in trace if isinstance(item, dict)]
        print(f"LangGraph nodes executed: {', '.join(nodes)}")
    print(f"Confidence: {confidence:.2f}")

    print("\nInput Logs:")
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
