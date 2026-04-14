import math
import os

import mlflow
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["metrics"])


def _safe(val, ndigits=4):
    """Return None for NaN/Inf, else round to ndigits."""
    if val is None or (isinstance(val, float) and not math.isfinite(val)):
        return None
    return round(float(val), ndigits)


@router.get("/metrics")
async def get_metrics():
    try:
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
        runs = mlflow.search_runs(experiment_names=["imdb_binary_classifier"])
        if runs.empty:
            return []

        results = []
        for _, row in runs.iterrows():
            name = row.get("tags.mlflow.runName", "")
            if not name:
                continue
            results.append({
                "name":              name,
                "accuracy":          _safe(row.get("metrics.accuracy")),
                "f1":                _safe(row.get("metrics.f1")),
                "roc_auc":           _safe(row.get("metrics.roc_auc")),
                "precision":         _safe(row.get("metrics.precision")),
                "recall":            _safe(row.get("metrics.recall")),
                "log_loss":          _safe(row.get("metrics.log_loss")),
                "mcc":               _safe(row.get("metrics.mcc")),
                "inference_ms":      _safe(row.get("metrics.inference_ms"), 3),
                "train_duration_sec":_safe(row.get("metrics.train_duration_sec"), 2),
                "ram_used_gb":       _safe(row.get("metrics.ram_used_gb"), 2),
                "ram_percent":       _safe(row.get("metrics.ram_percent"), 1),
                "cpu_percent":       _safe(row.get("metrics.cpu_percent"), 1),
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
