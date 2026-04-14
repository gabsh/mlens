import numpy as np
from sklearn.naive_bayes import MultinomialNB


class NBClassifier:
    name = "nb"
    supports_sparse = True  # MultinomialNB natively handles sparse matrices

    def __init__(self):
        self.model = MultinomialNB(alpha=0.1)

    def fit(self, X, y) -> "NBClassifier":
        self.model.fit(X, y)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        return self.model.predict_proba(X)
