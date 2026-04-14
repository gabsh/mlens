from sklearn.feature_extraction.text import TfidfVectorizer


class TFIDFEmbedder:
    name = "tfidf"
    is_sparse = True
    needs_raw_text = False

    def __init__(self, max_features: int = 50_000, ngram_range: tuple = (1, 2)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=True,   # log(1+tf) scaling — improves LR performance
            min_df=2,
        )

    def fit(self, texts: list[str]) -> "TFIDFEmbedder":
        self.vectorizer.fit(texts)
        return self

    def transform(self, texts: list[str]):
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: list[str]):
        return self.vectorizer.fit_transform(texts)
