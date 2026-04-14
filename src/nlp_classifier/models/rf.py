import numpy as np
from sklearn.ensemble import RandomForestClassifier


class RFClassifier:
    name = "rf"
    supports_sparse = False  # RandomForest requires dense arrays

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            n_jobs=-1,
            random_state=42,
        )

    def fit(self, X, y) -> "RFClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
