"""
Model registry: loads all .pkl models once at startup and routes predictions.
Designed to be instantiated once in FastAPI's lifespan context.
"""
import logging
from pathlib import Path

import joblib

from src.nlp_classifier.preprocessing import clean_text

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Loads all .pkl artifacts from model_dir at init time.
    Thread-safe for reads (no mutations after initialization).
    """

    def __init__(self, model_dir: str = "./models"):
        self._models: dict[str, dict] = {}
        self._load_all(Path(model_dir))

    def _load_all(self, model_dir: Path) -> None:
        pkl_files = list(model_dir.glob("*.pkl"))
        if not pkl_files:
            logger.warning(f"No .pkl files found in {model_dir}")
            return
        for pkl_path in pkl_files:
            try:
                artifact = joblib.load(pkl_path)
                self._models[pkl_path.stem] = artifact
                logger.info(f"Loaded model: {pkl_path.stem}")
            except Exception as e:
                logger.error(f"Failed to load {pkl_path}: {e}")

    def available_models(self) -> list[str]:
        return sorted(self._models.keys())

    def predict(self, model_name: str, text: str) -> dict:
        if model_name not in self._models:
            raise KeyError(f"Model '{model_name}' not found. Available: {self.available_models()}")

        artifact = self._models[model_name]
        embedder = artifact["embedder"]
        classifier = artifact["classifier"]

        X = embedder.transform([clean_text(text)])

        if hasattr(X, "toarray") and not classifier.supports_sparse:
            X = X.toarray()

        label_idx = int(classifier.predict(X)[0])
        proba = classifier.predict_proba(X)[0].tolist()

        return {
            "label": artifact["label_names"][label_idx],
            "label_idx": label_idx,
            "confidence": proba[label_idx],
            "probabilities": {
                name: prob
                for name, prob in zip(artifact["label_names"], proba)
            },
        }
