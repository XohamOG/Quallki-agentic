from __future__ import annotations

import json

import streamlit as st

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.healthcare.demo_runner import run_alert_payload, run_healthcare_demo_scenario


st.set_page_config(page_title="QUAL-KI Healthcare SOC Demo", layout="wide")

st.title("QUAL-KI Agentic Healthcare SOC Demo")
st.caption(
    "Scenario-driven hospital cybersecurity demonstration with agentic triage, containment, and compliance evidence."
)

input_mode = st.sidebar.radio("Input source", ["Live JSON/JSONL", "Synthetic demo"], index=0)
scenario_key = None
uploaded_file = None
if input_mode == "Synthetic demo":
    scenario_key = st.sidebar.selectbox(
        "Select Hospital Scenario",
        options=sorted(HOSPITAL_DEMO_CASES.keys()),
        index=0,
    )
else:
    uploaded_file = st.sidebar.file_uploader("Upload alert JSON or JSONL", type=["json", "jsonl", "txt"])

if st.sidebar.button("Run Agentic SOC"):
    if input_mode == "Synthetic demo" and scenario_key:
        st.session_state["run_data"] = run_healthcare_demo_scenario(scenario_key)
        st.session_state["run_mode"] = input_mode
    elif uploaded_file is not None:
        raw_text = uploaded_file.getvalue().decode("utf-8").strip()
        try:
            parsed = json.loads(raw_text)
            record = parsed[0] if isinstance(parsed, list) else parsed
            if not isinstance(record, dict):
                raise ValueError("The uploaded JSON must contain an object or a list of objects")
            st.session_state["run_data"] = run_alert_payload(record)
            st.session_state["run_mode"] = input_mode
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            st.error(f"Could not load alert input: {exc}")

run_data = st.session_state.get("run_data") if st.session_state.get("run_mode") == input_mode else None
if run_data is None:
    if input_mode == "Synthetic demo" and scenario_key:
        run_data = run_healthcare_demo_scenario(scenario_key)
    else:
        st.info("Upload a real JSON/JSONL alert and click Run Agentic SOC.")
        st.stop()

result = run_data["result"]
scenario = run_data["scenario"]
alert = result.get("alert_object", {})
triage = result.get("triage_result", {})
threat_intel = result.get("threat_intel_result", {})
response_actions = result.get("response_actions", [])
assignments = result.get("assignments", [])
forensics_summary = result.get("forensics_summary", "")
checklist = result.get("compliance_checklist", [])
compliance_assessment = result.get("compliance_assessment", {})

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Label", str(run_data["label"]))
metric_col2.metric("Confidence", f"{float(run_data['confidence']):.2f}")
metric_col3.metric("Priority", str(triage.get("priority", "P4")) if isinstance(triage, dict) else "P4")
metric_col4.metric("Scenario", run_data["scenario_key"])
st.caption(f"Inference backend: {run_data.get('qml_backend', 'unknown')}")

(
    tab_overview,
    tab_detection,
    tab_comparison,
    tab_triage,
    tab_threat_intel,
    tab_response,
    tab_forensics,
    tab_compliance,
    tab_workflow,
    tab_summary,
) = st.tabs(
    [
        "Overview",
        "Detection",
        "Model Comparison",
        "Triage",
        "Threat Intel",
        "Response",
        "Forensics",
        "Compliance",
        "LangGraph Trace",
        "SOC Summary",
    ]
)

with tab_overview:
    st.subheader(str(scenario.get("title", run_data["scenario_key"])))
    st.write(str(scenario.get("message", "")))
    st.write(
        {
            "asset_type": scenario.get("asset_type"),
            "contains_phi": scenario.get("contains_phi"),
            "clinical_impact": scenario.get("clinical_impact"),
            "source_ip": scenario.get("source_ip"),
            "simulation": run_data.get("payload", {}).get("simulation", {}),
        }
    )
    st.subheader("Simulated Attack Logs")
    st.code("\n".join(run_data.get("logs", [])) or "No logs generated.", language="text")

    analysis = alert.get("analysis", {}) if isinstance(alert, dict) else {}
    cwss = alert.get("cwss", {}) if isinstance(alert, dict) else {}
    st.subheader("Detection Evidence")
    st.json(
        {
            "attack_vector": analysis.get("attack_vector", "unknown"),
            "evidence": analysis.get("evidence", []),
            "iocs": analysis.get("iocs", []),
            "likely_cwes": analysis.get("likely_cwes", []),
            "cwss_score": cwss.get("score", 0.0),
        }
    )

with tab_detection:
    st.subheader("Detection Agent Output")
    st.caption("Local autoencoder + VQC inference, log analysis, IOC extraction, and severity scoring.")
    st.json(alert if isinstance(alert, dict) else {})

with tab_comparison:
    st.subheader("Quantum vs Classical Model Comparison")
    st.caption("Live inference comparison between the 6-qubit QML VQC and the LightGBM Classical Model.")
    
    qml_label = alert.get("qml_label", "unknown") if isinstance(alert, dict) else "unknown"
    classical_label = alert.get("classical_label", "unknown") if isinstance(alert, dict) else "unknown"
    backend = alert.get("qml_backend", "unknown") if isinstance(alert, dict) else "unknown"
    
    col_qml, col_classical = st.columns(2)
    with col_qml:
        st.info("### Quantum VQC Model")
        st.metric("Prediction", str(qml_label))
        st.caption(f"Backend: `{backend}`")
        if qml_label != "unknown":
            st.success("Quantum Model actively deployed.")
            
    with col_classical:
        st.info("### Classical LightGBM Model")
        st.metric("Prediction", str(classical_label))
        st.caption(f"Backend: `best_regularized_model.joblib`")
        if classical_label == "unknown":
            st.warning("Classical model prediction unavailable.")
        elif classical_label != qml_label:
            st.warning("Model Disagreement!")
        else:
            st.success("Models agree on prediction.")

with tab_workflow:
    st.subheader("LangGraph Execution Trace")
    st.caption("Each entry is the state update returned by a real graph node for this run.")
    trace = run_data.get("workflow_trace", [])
    if isinstance(trace, list) and trace:
        for index, entry in enumerate(trace, start=1):
            if not isinstance(entry, dict):
                continue
            node = str(entry.get("node", "unknown"))
            with st.expander(f"{index}. {node}", expanded=index == 1):
                st.json(entry.get("output", {}))
    else:
        st.info("No streamed graph updates available.")

with tab_triage:
    st.subheader("Triage Reasoning")
    if isinstance(triage, dict):
        st.write(
            {
                "priority": triage.get("priority"),
                "confidence": triage.get("confidence"),
                "reasoning": triage.get("reasoning"),
                "reasoning_backend": triage.get("reasoning_backend", "deterministic"),
                "recommended_fixes": triage.get("recommended_fixes", []),
                "auto_close": triage.get("auto_close"),
            }
        )
    else:
        st.info("No triage details available")

with tab_threat_intel:
    st.subheader("Threat Intelligence Agent Output")
    st.json(threat_intel if isinstance(threat_intel, dict) else {})

with tab_response:
    st.subheader("Response Agent Output")
    if isinstance(assignments, list) and assignments:
        st.write({"assignments": assignments})
    if isinstance(response_actions, list) and response_actions:
        for index, action in enumerate(response_actions, start=1):
            st.write(f"{index}. {action}")
    else:
        st.info("No containment actions generated")

with tab_forensics:
    st.subheader("Forensics Agent Output")
    st.write(forensics_summary or "No forensics summary generated.")

with tab_compliance:
    st.subheader("Compliance Evidence Mapping")
    st.warning(
        "This is a control-to-evidence mapping, not a compliance certification. "
        "Open each source and have the named control owner validate the required evidence."
    )
    if isinstance(compliance_assessment, dict):
        st.write(compliance_assessment)
    if isinstance(checklist, list) and checklist:
        st.dataframe(checklist, width="stretch")
    else:
        st.info("No compliance checklist available")

with tab_summary:
    st.subheader("Executive Incident Summary")
    st.write(str(result.get("final_summary", "No summary generated.")))
