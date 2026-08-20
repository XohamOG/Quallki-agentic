from __future__ import annotations

import streamlit as st

from quallki_agentic.healthcare import HOSPITAL_DEMO_CASES
from quallki_agentic.healthcare.demo_runner import run_healthcare_demo_scenario


st.set_page_config(page_title="QUAL-KI Healthcare SOC Demo", layout="wide")

st.title("QUAL-KI Agentic Healthcare SOC Demo")
st.caption(
    "Scenario-driven hospital cybersecurity demonstration with agentic triage, containment, and compliance evidence."
)

scenario_key = st.sidebar.selectbox(
    "Select Hospital Scenario",
    options=sorted(HOSPITAL_DEMO_CASES.keys()),
    index=0,
)

if st.sidebar.button("Run Agentic SOC"):
    st.session_state["run_data"] = run_healthcare_demo_scenario(scenario_key)

run_data = st.session_state.get("run_data")
if run_data is None:
    run_data = run_healthcare_demo_scenario(scenario_key)

result = run_data["result"]
scenario = run_data["scenario"]
triage = result.get("triage_result", {})
response_actions = result.get("response_actions", [])
checklist = result.get("compliance_checklist", [])

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Label", str(run_data["label"]))
metric_col2.metric("Confidence", f"{float(run_data['confidence']):.2f}")
metric_col3.metric("Priority", str(triage.get("priority", "P4")) if isinstance(triage, dict) else "P4")
metric_col4.metric("Scenario", run_data["scenario_key"])

tab_overview, tab_workflow, tab_triage, tab_response, tab_compliance, tab_summary = st.tabs(
    [
        "Overview",
        "Agentic Workflow",
        "Triage",
        "Containment",
        "Compliance",
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
        }
    )
    st.subheader("Simulated Attack Logs")
    st.code("\n".join(run_data.get("logs", [])) or "No logs generated.", language="text")

    alert = result.get("alert_object", {})
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

with tab_workflow:
    st.subheader("How the Agentic System Works")
    st.markdown(
        """
1. Detection Agent enriches incoming hospital security alert into a structured alert object.
2. Triage Agent scores priority and selects routing path.
3. Threat Intel Agent maps likely ATT&CK context.
4. Response Agent proposes containment actions with clinical safety checks.
5. Forensics Agent prepares timeline context for incident review.
6. Compliance Agent generates HIPAA/GDPR/ISO27001/SOC2/NIS2 checklist evidence.
        """
    )

with tab_triage:
    st.subheader("Triage Reasoning")
    if isinstance(triage, dict):
        st.write(
            {
                "priority": triage.get("priority"),
                "confidence": triage.get("confidence"),
                "reasoning": triage.get("reasoning"),
                "auto_close": triage.get("auto_close"),
            }
        )
    else:
        st.info("No triage details available")

with tab_response:
    st.subheader("Containment Actions")
    if isinstance(response_actions, list) and response_actions:
        for index, action in enumerate(response_actions, start=1):
            st.write(f"{index}. {action}")
    else:
        st.info("No containment actions generated")

with tab_compliance:
    st.subheader("SOC Compliance Checklist")
    if isinstance(checklist, list) and checklist:
        st.dataframe(checklist, width="stretch")
    else:
        st.info("No compliance checklist available")

with tab_summary:
    st.subheader("Executive Incident Summary")
    st.write(str(result.get("final_summary", "No summary generated.")))
