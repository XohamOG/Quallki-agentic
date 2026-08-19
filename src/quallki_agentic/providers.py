from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from quallki_agentic.config import Settings
from quallki_agentic.state import ClassificationResult


class AlertClassifier(Protocol):
    def classify(self, text: str) -> ClassificationResult:
        ...


class IncidentResponder(Protocol):
    def respond(
        self,
        alert: str,
        classification: ClassificationResult,
        context_snippets: list[str],
    ) -> str:
        ...


@dataclass
class KeywordClassifier:
    """Baseline classifier until your production ML model is plugged in."""

    model_path: str

    def classify(self, text: str) -> ClassificationResult:
        lowered = text.lower()

        if any(token in lowered for token in ["ransomware", "encrypt", "exfiltration"]):
            return ClassificationResult("malware", "critical", 0.84)
        if any(token in lowered for token in ["bruteforce", "failed login", "credential"]):
            return ClassificationResult("identity_attack", "high", 0.79)
        if any(token in lowered for token in ["scan", "port", "recon"]):
            return ClassificationResult("reconnaissance", "medium", 0.73)

        return ClassificationResult("unknown", "low", 0.51)


class TemplateResponder:
    def respond(
        self,
        alert: str,
        classification: ClassificationResult,
        context_snippets: list[str],
    ) -> str:
        context = "\n".join(f"- {snippet}" for snippet in context_snippets) or "- No context found"
        return (
            f"Incident Summary\n"
            f"Alert: {alert}\n"
            f"Type: {classification.label}\n"
            f"Severity: {classification.severity}\n"
            f"Confidence: {classification.confidence:.2f}\n\n"
            f"Context\n{context}\n\n"
            f"Recommended immediate actions:\n"
            f"1. Validate source host and account activity.\n"
            f"2. Isolate affected endpoints if malicious behavior is confirmed.\n"
            f"3. Preserve logs and artifacts for triage and forensics."
        )


class OpenAIResponder:
    def __init__(self, model_name: str) -> None:
        from langchain_openai import ChatOpenAI

        self._llm = ChatOpenAI(model=model_name, temperature=0)

    def respond(
        self,
        alert: str,
        classification: ClassificationResult,
        context_snippets: list[str],
    ) -> str:
        context = "\n".join(context_snippets) if context_snippets else "No context found."
        prompt = (
            "You are a SOC copilot. Produce concise triage output with: summary, "
            "risk rationale, and next three actions.\n\n"
            f"Alert: {alert}\n"
            f"Classification: {classification.label}\n"
            f"Severity: {classification.severity}\n"
            f"Confidence: {classification.confidence:.2f}\n"
            f"Context:\n{context}"
        )
        return self._llm.invoke(prompt).content


def build_classifier(settings: Settings) -> AlertClassifier:
    model_path = settings.local_classifier_model_path
    if not os.path.exists(model_path):
        # Keep startup resilient while model artifacts are being prepared.
        return KeywordClassifier(model_path=model_path)
    return KeywordClassifier(model_path=model_path)


def build_responder(settings: Settings) -> IncidentResponder:
    if settings.use_openai and os.getenv("OPENAI_API_KEY"):
        return OpenAIResponder(model_name=settings.openai_model)
    return TemplateResponder()
