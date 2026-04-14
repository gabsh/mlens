import numpy as np
from xgboost import XGBClassifier as _XGBClassifier


class XGBClassifier:
    name = "xgb"
    supports_sparse = True  # XGBoost handles scipy sparse natively

    def __init__(self):
        self.model = _XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            n_jobs=-1,
            random_state=42,
            eval_metric="logloss",
            verbosity=0,
        )

    def fit(self, X, y) -> "XGBClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
