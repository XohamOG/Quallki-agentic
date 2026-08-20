from quallki_agentic.config import Settings
from quallki_agentic.qml_model import QMLVQCClassifier

settings = Settings.from_env()
clf = QMLVQCClassifier(
    settings.qml_model_path,
    settings.qml_autoencoder_path,
    settings.qml_preprocessing_path,
)
print("Available:", clf.available)
if not clf.available:
    print("Error:", clf.load_error)
