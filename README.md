# Quallki Agentic (QUAL-KI v2 SOC Starter)

This repository now includes a roadmap-aligned LangGraph SOC architecture scaffold for QUAL-KI v2.0.

Current workflow (implemented):

1. Ingest and normalize alert text.
2. Simulate QML verdict bridge (label + confidence).
3. Detection Agent enriches alert into AlertObject.
4. Triage Agent assigns priority and route.
5. Threat Intel Agent maps basic ATT&CK context.
6. Response, Forensics, and Compliance agents finalize actions and summary.

## Prerequisites

- Python 3.11+

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -e .
```

Alternative install path:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set API keys.

## Quick start

Run the healthcare SOC demo graph:

```bash
python -m app --scenario ehr_ransomware
```

Try another hospital scenario:

```bash
python -m app --scenario radiology_recon
```

Available demo scenarios:

- `ehr_ransomware`
- `radiology_recon`
- `infusion_pump_access`

## Compliance Scope (Demo)

The compliance tab/checklist now maps SOC operations to:

- HIPAA Security Rule
- GDPR (Article 32 and 33)
- ISO/IEC 27001:2022
- SOC 2 (CC7)
- NIS2 reporting readiness
- NIST CSF / NIST SP 800-66

## Runtime Configuration

Set in `.env`:

- `LLM_PROVIDER=gemini`
- `GEMINI_API_KEY=...`
- `GEMINI_MODEL=gemini-2.5-pro`
- `DEMO_MODE=true`
- `DOMAIN_PROFILE=healthcare`
- `ENABLE_EVENT_BUS=false`
- `MESSAGE_BUS_BACKEND=inmemory`
- `REDIS_URL=redis://localhost:6379/0`
- `REDIS_STREAM_NAME=qualki.events`
- `CLASSICAL_MODEL_PATH=best_regularized_model.joblib`

For this demo mode, no external Redis/message broker is required.

## Current Detection Backend

Until QML artifacts are ready, the system uses your attached classical model file:

- `best_regularized_model.joblib`

The detection bridge auto-loads this model and uses it for inference fallback in the pipeline.

## Architecture

- `src/quallki_agentic/config.py` holds environment-driven runtime settings.
- `src/quallki_agentic/agents/` contains SOC role modules (detection, triage, threat intel, response, forensics, deception, vuln, compliance).
- `src/quallki_agentic/orchestrator/` contains shared schemas, state, routing edges, and LangGraph workflow.
- `src/quallki_agentic/quantum/` contains QML integration bridge stubs.
- `src/quallki_agentic/crypto/` contains PQC/QKD message security scaffolding.
- `src/quallki_agentic/telemetry/` contains ingestion and time-window utilities.

## Where to add your assets

- Put your local classification model artifacts under `models/classifier` (or set `LOCAL_CLASSIFIER_MODEL_PATH`).
- Put SOC runbooks/playbooks in markdown files under `knowledge/`.
- Set `USE_OPENAI=true` and keys in `.env` to enable LLM-generated response drafting.

## Roadmap Status

- Phase 0 scaffolding: in progress (module structure created).
- Phase 1 core pipeline: implemented in runnable form.
- Phase 2 triage + threat intel baseline: implemented with Gemini-capable triage and heuristic fallback.
- Phase 3+ modules (response hardening, forensics depth, QKD production simulation, deception/vuln/compliance integrations): scaffolded and ready for integration.

## Next Build Targets

1. Replace feature stub in model inference with real feature vectorization from your cleaned dataset pipeline.
2. Add Redis consumer workers so specialist agents can run in separate processes.
3. Add FastAPI inference service wrapping current classical model and later QML endpoint swap.
4. Extend the Streamlit UI with analyst decision logging and downloadable compliance evidence bundle.

## UI Demo

Run the demo web app:

```bash
streamlit run src/quallki_agentic/ui/streamlit_app.py
```

Tabs included:

- Overview
- Agentic Workflow (explainer)
- Triage
- Containment
- Compliance
- SOC Summary
