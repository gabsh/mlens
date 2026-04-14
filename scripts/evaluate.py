"""
Load all saved .pkl models and re-evaluate on the test set.
Prints a comparison table sorted by ROC-AUC.

Usage:
  python scripts/evaluate.py
"""
import os
import sys
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp_classifier.preprocessing import clean_text

load_dotenv()


def evaluate_model(artifact: dict, X_test_clean: list, y_test: list) -> dict:
    embedder = artifact["embedder"]
    classifier = artifact["classifier"]

    X = embedder.transform(X_test_clean)

    if hasattr(X, "toarray") and not classifier.supports_sparse:
        X = X.toarray()

    y_pred = classifier.predict(X)
    y_proba = classifier.predict_proba(X)[:, 1]

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
    }


def main():
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    model_dir = Path(os.getenv("MODEL_DIR", "./models"))

    print("Loading test data...")
    test_df = pd.read_parquet(data_dir / "raw" / "test.parquet")
    X_test_clean = [clean_text(t) for t in test_df["text"]]
    y_test = test_df["label"].tolist()
    print(f"  {len(y_test)} test samples")

    pkl_files = sorted(model_dir.glob("*.pkl"))
    if not pkl_files:
        print(f"No .pkl files found in {model_dir}")
        return

    results = []
    for pkl_path in pkl_files:
        print(f"Evaluating {pkl_path.stem}...")
        artifact = joblib.load(pkl_path)
        try:
            metrics = evaluate_model(artifact, X_test_clean, y_test)
            metrics["model"] = pkl_path.stem
            results.append(metrics)
        except Exception as e:
            print(f"  ERROR: {e}")

    if results:
        print("\n=== Evaluation Results ===")
        print(f"{'Model':<25} {'Accuracy':>10} {'F1':>10} {'ROC-AUC':>10}")
        print("-" * 57)
        for r in sorted(results, key=lambda x: x["roc_auc"], reverse=True):
            print(f"{r['model']:<25} {r['accuracy']:>10.4f} {r['f1']:>10.4f} {r['roc_auc']:>10.4f}")


if __name__ == "__main__":
    main()
