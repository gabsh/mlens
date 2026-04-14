import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC


class SVMClassifier:
    name = "svm"
    supports_sparse = True  # LinearSVC handles scipy sparse matrices

    def __init__(self):
        # CalibratedClassifierCV wraps LinearSVC to enable predict_proba
        self.model = CalibratedClassifierCV(LinearSVC(max_iter=2000), cv=3)

    def fit(self, X, y) -> "SVMClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
