import numpy as np
from sklearn.neural_network import MLPClassifier as _MLPClassifier


class MLPClassifier:
    name = "mlp"
    supports_sparse = False  # sklearn MLP requires dense arrays

    def __init__(self):
        self.model = _MLPClassifier(
            hidden_layer_sizes=(256, 128),
            activation="relu",
            max_iter=200,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42,
        )

    def fit(self, X, y) -> "MLPClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
