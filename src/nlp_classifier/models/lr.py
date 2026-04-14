import numpy as np
from sklearn.linear_model import LogisticRegression


class LRClassifier:
    name = "lr"
    supports_sparse = True  # sklearn LR handles scipy sparse matrices

    def __init__(self):
        self.model = LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
            n_jobs=-1,
        )

    def fit(self, X, y) -> "LRClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
