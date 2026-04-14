import numpy as np


class GloVeEmbedder:
    """
    GloVe pretrained vectors (no training on the dataset).
    fit() loads the vectors from disk; transform() computes mean pooling.

    The GloVe file must be downloaded separately:
      python scripts/download_data.py
    """

    name = "glove"
    is_sparse = False
    needs_raw_text = False

    def __init__(
        self,
        glove_path: str = "data/raw/glove.6B.100d.txt",
        vector_size: int = 100,
    ):
        self.glove_path = glove_path
        self.vector_size = vector_size
        self._embeddings: dict[str, np.ndarray] = {}

    def fit(self, texts=None) -> "GloVeEmbedder":
        """Load pretrained GloVe vectors from disk (texts argument ignored)."""
        self._embeddings = {}
        with open(self.glove_path, encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                word = parts[0]
                vec = np.array(parts[1:], dtype=np.float32)
                self._embeddings[word] = vec
        return self

    def _doc_vector(self, text: str) -> np.ndarray:
        tokens = text.split()
        vecs = [self._embeddings[t] for t in tokens if t in self._embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(self.vector_size, dtype=np.float32)

    def transform(self, texts: list[str]) -> np.ndarray:
        return np.vstack([self._doc_vector(t) for t in texts])

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        return self.fit().transform(texts)
