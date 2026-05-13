"""
Train all embedding × classifier combinations on the IMDB dataset.
Each combination = one MLflow run + one exported .pkl artifact.

Usage:
  python scripts/train.py
  python scripts/train.py --embeddings tfidf bow --classifiers lr svm
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

import numpy as np
import psutil
import time

import joblib
import mlflow
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score, log_loss,
    matthews_corrcoef, precision_score, recall_score, roc_auc_score, roc_curve,
)

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp_classifier.embeddings.bow import BoWEmbedder
from src.nlp_classifier.embeddings.glove import GloVeEmbedder
from src.nlp_classifier.embeddings.tfidf import TFIDFEmbedder
from src.nlp_classifier.models.lgbm import LGBMClassifier
from src.nlp_classifier.models.lr import LRClassifier
from src.nlp_classifier.models.mlp import MLPClassifier
from src.nlp_classifier.models.nb import NBClassifier
from src.nlp_classifier.models.rf import RFClassifier
from src.nlp_classifier.models.svm import SVMClassifier
from src.nlp_classifier.models.xgb import XGBClassifier
from src.nlp_classifier.preprocessing import preprocess_df

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EMBEDDER_REGISTRY = {
    "tfidf": TFIDFEmbedder,
    "bow": BoWEmbedder,
    "glove": GloVeEmbedder,
}

# Combinations that cannot train: (embedder, classifier)
# NB requires non-negative features — incompatible with GloVe (dense, can be negative)
INCOMPATIBLE = {("glove", "nb")}

CLASSIFIER_REGISTRY = {
    "lr": LRClassifier,
    "svm": SVMClassifier,
    "rf": RFClassifier,
    "lgbm": LGBMClassifier,
    "mlp": MLPClassifier,
    "nb": NBClassifier,
    "xgb": XGBClassifier,
}


def load_data(data_dir: Path, max_train_samples: int | None = None):
    train_df = pd.read_parquet(data_dir / "raw" / "train.parquet")
    test_df = pd.read_parquet(data_dir / "raw" / "test.parquet")

    if max_train_samples:
        train_df = train_df.sample(n=min(max_train_samples, len(train_df)), random_state=42)

    train_df = preprocess_df(train_df)
    test_df = preprocess_df(test_df)

    return (
        train_df["text"].tolist(),       # raw text
        train_df["text_clean"].tolist(), # cleaned text
        test_df["text"].tolist(),
        test_df["text_clean"].tolist(),
        train_df["label"].tolist(),
        test_df["label"].tolist(),
    )


def train_one(
    embedder,
    classifier,
    X_tr_vec,
    X_te_vec,
    y_train, y_test,
    model_dir: Path,
) -> dict:
    run_name = f"{embedder.name}_{classifier.name}"
    logger.info(f"Starting run: {run_name}")

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag("embedding", embedder.name)
        mlflow.set_tag("classifier", classifier.name)
        mlflow.log_param("embedder", embedder.name)
        mlflow.log_param("classifier", classifier.name)

        # Densify if classifier cannot handle sparse
        if embedder.is_sparse and not classifier.supports_sparse:
            X_tr_vec = X_tr_vec.toarray()
            X_te_vec = X_te_vec.toarray()

        # Train
        logger.info(f"  Training {classifier.name}...")
        t0 = time.time()
        classifier.fit(X_tr_vec, y_train)
        train_duration = time.time() - t0

        # Evaluate
        y_pred = classifier.predict(X_te_vec)
        y_proba = classifier.predict_proba(X_te_vec)[:, 1]

        acc  = float(accuracy_score(y_test, y_pred))
        f1   = float(f1_score(y_test, y_pred))
        auc  = float(roc_auc_score(y_test, y_proba))
        prec = float(precision_score(y_test, y_pred))
        rec  = float(recall_score(y_test, y_pred))
        ll   = float(log_loss(y_test, y_proba))
        mcc  = float(matthews_corrcoef(y_test, y_pred))

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        idx = np.linspace(0, len(fpr) - 1, 150, dtype=int)

        # Inference speed: time to predict a single sample
        t_inf = time.time()
        classifier.predict(X_te_vec[:1])
        inf_ms = round((time.time() - t_inf) * 1000, 3)

        # Hardware metrics
        ram = psutil.virtual_memory()
        cpu_pct = psutil.cpu_percent(interval=1)

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1", f1)
        mlflow.log_metric("roc_auc", auc)
        mlflow.log_metric("precision", prec)
        mlflow.log_metric("recall", rec)
        mlflow.log_metric("log_loss", ll)
        mlflow.log_metric("mcc", mcc)
        mlflow.log_metric("inference_ms", inf_ms)
        mlflow.log_metric("train_duration_sec", round(train_duration, 2))
        mlflow.log_metric("cpu_percent", cpu_pct)
        mlflow.log_metric("ram_used_gb", round(ram.used / 1e9, 2))
        mlflow.log_metric("ram_percent", ram.percent)

        mlflow.log_text(classification_report(y_test, y_pred), "classification_report.txt")

        # Export .pkl
        model_dir.mkdir(parents=True, exist_ok=True)
        artifact = {
            "embedder": embedder,
            "classifier": classifier,
            "embedder_name": embedder.name,
            "classifier_name": classifier.name,
            "label_names": ["negative", "positive"],
        }
        pkl_path = model_dir / f"{run_name}.pkl"
        joblib.dump(artifact, pkl_path)
        mlflow.log_artifact(str(pkl_path))

        logger.info(f"  [{run_name}] acc={acc:.4f}  f1={f1:.4f}  auc={auc:.4f}  mcc={mcc:.4f}  → {pkl_path}")
        return {
            "run_name": run_name,
            "accuracy": acc, "f1": f1, "roc_auc": auc, "mcc": mcc,
            "fpr": fpr[idx].tolist(), "tpr": tpr[idx].tolist(),
        }


def main():
    parser = argparse.ArgumentParser(description="Train NLP classifier combinations")
    parser.add_argument(
        "--embeddings", nargs="+",
        choices=list(EMBEDDER_REGISTRY),
        default=list(EMBEDDER_REGISTRY),
        help="Embeddings to run (default: all)",
    )
    parser.add_argument(
        "--classifiers", nargs="+",
        choices=list(CLASSIFIER_REGISTRY),
        default=list(CLASSIFIER_REGISTRY),
        help="Classifiers to run (default: all)",
    )
    parser.add_argument(
        "--max-train-samples", type=int, default=None,
        help="Subsample training set (useful for BERT speed testing)",
    )
    args = parser.parse_args()

    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    model_dir = Path(os.getenv("MODEL_DIR", "./models"))

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("imdb_binary_classifier")

    logger.info("Loading data...")
    X_train_raw, X_train_clean, X_test_raw, X_test_clean, y_train, y_test = load_data(
        data_dir, max_train_samples=args.max_train_samples
    )
    logger.info(f"  Train: {len(X_train_raw)} | Test: {len(X_test_raw)}")

    results = []
    for emb_name in args.embeddings:
        # Build embedder
        if emb_name == "glove":
            glove_path = data_dir / "raw" / "glove.6B.100d.txt"
            if not glove_path.exists():
                logger.warning(f"GloVe file not found at {glove_path}, skipping.")
                continue
            embedder = GloVeEmbedder(glove_path=str(glove_path))
        else:
            embedder = EMBEDDER_REGISTRY[emb_name]()

        # Embed once for all classifiers
        X_tr = X_train_raw if embedder.needs_raw_text else X_train_clean
        X_te = X_test_raw  if embedder.needs_raw_text else X_test_clean
        logger.info(f"Fitting embedder {emb_name} on {len(X_tr)} samples...")
        try:
            X_tr_vec = embedder.fit_transform(X_tr)
            X_te_vec = embedder.transform(X_te)
        except Exception as e:
            logger.error(f"Failed to embed with {emb_name}: {e}")
            continue

        for clf_name in args.classifiers:
            if (emb_name, clf_name) in INCOMPATIBLE:
                logger.warning(f"Skipping incompatible combination: {emb_name}+{clf_name}")
                continue
            classifier = CLASSIFIER_REGISTRY[clf_name]()
            try:
                result = train_one(
                    embedder, classifier,
                    X_tr_vec, X_te_vec,
                    y_train, y_test,
                    model_dir,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"  Failed {emb_name}_{clf_name}: {e}")

    if results:
        print("\n=== Results summary ===")
        print(f"{'Model':<25} {'Accuracy':>10} {'F1':>10} {'ROC-AUC':>10} {'MCC':>10}")
        print("-" * 67)
        for r in sorted(results, key=lambda x: x["roc_auc"], reverse=True):
            print(f"{r['run_name']:<25} {r['accuracy']:>10.4f} {r['f1']:>10.4f} {r['roc_auc']:>10.4f} {r['mcc']:>10.4f}")

        new_roc = {
            r["run_name"]: {"name": r["run_name"], "fpr": r["fpr"], "tpr": r["tpr"], "auc": round(r["roc_auc"], 4)}
            for r in results
        }
        roc_path = model_dir / "roc_curves.json"
        if roc_path.exists():
            existing = {e["name"]: e for e in json.loads(roc_path.read_text())}
            existing.update(new_roc)
            new_roc = existing
        roc_path.write_text(json.dumps(list(new_roc.values())))
        print(f"\nROC curves saved to {roc_path}")


if __name__ == "__main__":
    main()
