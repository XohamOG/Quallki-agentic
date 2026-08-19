# Healthcare SOC Demo UI Plan

## Goal
Build a simple web UI for hospital cybersecurity SOC demonstrations using the existing orchestrator pipeline.

## Recommended Stack
- Streamlit for fastest demo delivery.

## Screens
1. Scenario Picker
- Choose from ehr_ransomware, radiology_recon, infusion_pump_access.

2. Triage Panel
- Show predicted label, confidence, priority, and reasoning.

3. Containment Actions Panel
- Show ordered response actions with clinical safety annotations.

4. Compliance Checklist Panel
- Show HIPAA/NIST checklist with done/pending state.

5. Incident Summary Panel
- Show final orchestrator summary and ATT&CK mapping.

## Integration Contract
- Input: scenario key string.
- Backend call: orchestrator graph invoke(payload).
- Output keys used by UI:
  - triage_result
  - response_actions
  - compliance_checklist
  - final_summary

## Next Implementation
- Create src/quallki_agentic/ui/streamlit_app.py
- Add "streamlit" to requirements
- Add run command: streamlit run src/quallki_agentic/ui/streamlit_app.py
