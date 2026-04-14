"""
Text normalization pipeline used by all non-BERT embeddings.
BERT embedders bypass this and receive raw text directly.
"""
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

_STOP_WORDS = set(stopwords.words("english"))
_STEMMER = PorterStemmer()


def clean_text(text: str, stem: bool = False, remove_stopwords: bool = True) -> str:
    """
    Normalize a raw text string:
    - Lowercase
    - Strip HTML tags (IMDB has <br /> tags)
    - Remove non-alphabetic characters
    - Normalize whitespace
    - Optionally remove English stopwords
    - Optionally apply Porter stemming
    """
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)       # strip HTML
    text = re.sub(r"[^a-z\s]", " ", text)       # keep only letters
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return ""

    tokens = text.split()
    if remove_stopwords:
        tokens = [t for t in tokens if t not in _STOP_WORDS]
    if stem:
        tokens = [_STEMMER.stem(t) for t in tokens]
    return " ".join(tokens)


def preprocess_df(df, stem: bool = False, remove_stopwords: bool = True):
    """Add a 'text_clean' column to a DataFrame with a 'text' column."""
    df = df.copy()
    df["text_clean"] = df["text"].apply(
        lambda t: clean_text(t, stem=stem, remove_stopwords=remove_stopwords)
    )
    return df
