from sklearn.feature_extraction.text import CountVectorizer


class BoWEmbedder:
    name = "bow"
    is_sparse = True
    needs_raw_text = False

    def __init__(self, max_features: int = 50_000):
        self.vectorizer = CountVectorizer(
            max_features=max_features,
            ngram_range=(1, 1),
            min_df=2,
        )

    def fit(self, texts: list[str]) -> "BoWEmbedder":
        self.vectorizer.fit(texts)
        return self

    def transform(self, texts: list[str]):
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: list[str]):
        return self.vectorizer.fit_transform(texts)
