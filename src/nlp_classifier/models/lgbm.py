import numpy as np
from lightgbm import LGBMClassifier as _LGBMClassifier


class LGBMClassifier:
    name = "lgbm"
    supports_sparse = False  # LightGBM needs dense or its own sparse format

    def __init__(self):
        self.model = _LGBMClassifier(
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=63,
            n_jobs=-1,
            random_state=42,
            verbose=-1,
        )

    def fit(self, X, y) -> "LGBMClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
