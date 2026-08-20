from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = "quallki-agentic"
    demo_mode: bool = True
    enable_event_bus: bool = False
    domain_profile: str = "healthcare"
    llm_provider: str = "none"
    gemini_model: str = "gemini-3.5-flash"
    use_openai: bool = False
    use_gemini: bool = True
    openai_model: str = "gpt-4o-mini"
    message_bus_backend: str = "redis"
    redis_url: str = "redis://localhost:6379/0"
    redis_stream_name: str = "qualki.events"
    knowledge_dir: str = "knowledge"
    local_classifier_model_path: str = "models/classifier"
    qml_model_path: str = "best_qml_vqc_6q.pt"
    qml_autoencoder_path: str = "best_qml_autoencoder_6q.pt"
    qml_preprocessing_path: str = "qml_preprocessing.json"
    model_label_list: str = "BaseLine,Alice2,DevEva,Discov,Hulk,Nmap,NosyN,Ransac,SlowLoris,SuperSpy"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        langsmith_enabled = os.getenv("ENABLE_LANGSMITH", "false").strip().lower()
        if langsmith_enabled not in {"1", "true", "yes", "on"}:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
        use_openai_raw = os.getenv("USE_OPENAI", "false").strip().lower()
        use_openai = use_openai_raw in {"1", "true", "yes", "on"}
        use_gemini_raw = os.getenv("USE_GEMINI", "false").strip().lower()
        use_gemini = use_gemini_raw in {"1", "true", "yes", "on"}
        demo_mode_raw = os.getenv("DEMO_MODE", "true").strip().lower()
        demo_mode = demo_mode_raw in {"1", "true", "yes", "on"}
        event_bus_raw = os.getenv("ENABLE_EVENT_BUS", "false").strip().lower()
        enable_event_bus = event_bus_raw in {"1", "true", "yes", "on"}

        return cls(
            app_name=os.getenv("APP_NAME", "quallki-agentic"),
            demo_mode=demo_mode,
            enable_event_bus=enable_event_bus,
            domain_profile=os.getenv("DOMAIN_PROFILE", "healthcare"),
            llm_provider=os.getenv("LLM_PROVIDER", "none"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
            use_openai=use_openai,
            use_gemini=use_gemini,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            message_bus_backend=os.getenv("MESSAGE_BUS_BACKEND", "redis"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            redis_stream_name=os.getenv("REDIS_STREAM_NAME", "qualki.events"),
            knowledge_dir=os.getenv("KNOWLEDGE_DIR", "knowledge"),
            local_classifier_model_path=os.getenv(
                "LOCAL_CLASSIFIER_MODEL_PATH", "models/classifier"
            ),
            qml_model_path=os.getenv("QML_MODEL_PATH", "best_qml_vqc_6q.pt"),
            qml_autoencoder_path=os.getenv(
                "QML_AUTOENCODER_PATH", "best_qml_autoencoder_6q.pt"
            ),
            qml_preprocessing_path=os.getenv(
                "QML_PREPROCESSING_PATH", "qml_preprocessing.json"
            ),
            model_label_list=os.getenv(
                "MODEL_LABEL_LIST",
                "BaseLine,Alice2,DevEva,Discov,Hulk,Nmap,NosyN,Ransac,SlowLoris,SuperSpy",
            ),
        )
