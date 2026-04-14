"""
LIME-based text explanation.
"""
import logging
from typing import TYPE_CHECKING

import numpy as np
from lime.lime_text import LimeTextExplainer

from src.nlp_classifier.preprocessing import clean_text

if TYPE_CHECKING:
    from src.nlp_classifier.inference import ModelRegistry

logger = logging.getLogger(__name__)


class TextExplainer:
    def __init__(self, class_names: tuple = ("negative", "positive")):
        self.explainer = LimeTextExplainer(class_names=list(class_names))

    def explain(
        self,
        text: str,
        model_name: str,
        registry: "ModelRegistry",
        num_features: int = 10,
        num_samples: int = 500,
    ) -> dict:
        artifact = registry._models.get(model_name)
        if artifact is None:
            raise KeyError(f"Model '{model_name}' not found.")

        embedder = artifact["embedder"]
        classifier = artifact["classifier"]

        def predict_fn(texts: list[str]) -> np.ndarray:
            """Callable for LIME: perturbed texts → probability array (N, 2)."""
            cleaned = [clean_text(t) for t in texts]
            X = embedder.transform(cleaned)
            if hasattr(X, "toarray") and not classifier.supports_sparse:
                X = X.toarray()
            return classifier.predict_proba(X)

        exp = self.explainer.explain_instance(
            text,
            predict_fn,
            num_features=num_features,
            num_samples=num_samples,
        )

        return {
            "explanation": exp.as_list(),  # [(word, weight), ...]
            "model_name": model_name,
        }
