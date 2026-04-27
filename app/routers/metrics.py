import math
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["metrics"])

MLRUNS_DIR = Path(os.getenv("MLRUNS_DIR", "/app/mlruns"))
_EXPERIMENT_NAME = "imdb_binary_classifier"


def _safe(val, ndigits=4):
    if val is None or (isinstance(val, float) and not math.isfinite(val)):
        return None
    return round(float(val), ndigits)


def _read_metric(run_dir: Path, metric: str):
    path = run_dir / "metrics" / metric
    if not path.exists():
        return None
    try:
        last_line = path.read_text().strip().splitlines()[-1]
        return float(last_line.split()[1])
    except Exception:
        return None


def _read_tag(run_dir: Path, tag: str) -> str:
    path = run_dir / "tags" / tag
    return path.read_text().strip() if path.exists() else ""


def _find_experiment_dir() -> Path | None:
    if not MLRUNS_DIR.exists():
        return None
    for exp_dir in MLRUNS_DIR.iterdir():
        if not exp_dir.is_dir() or exp_dir.name.startswith("."):
            continue
        meta = exp_dir / "meta.yaml"
        if meta.exists() and _EXPERIMENT_NAME in meta.read_text():
            return exp_dir
    return None


@router.get("/metrics")
async def get_metrics():
    try:
        exp_dir = _find_experiment_dir()
        if exp_dir is None:
            return []

        results = []
        for run_dir in exp_dir.iterdir():
            if not run_dir.is_dir():
                continue
            meta = run_dir / "meta.yaml"
            if not meta.exists() or "status: 3" not in meta.read_text():
                continue
            name = _read_tag(run_dir, "mlflow.runName")
            if not name:
                continue
            results.append({
                "name":               name,
                "accuracy":           _safe(_read_metric(run_dir, "accuracy")),
                "f1":                 _safe(_read_metric(run_dir, "f1")),
                "roc_auc":            _safe(_read_metric(run_dir, "roc_auc")),
                "precision":          _safe(_read_metric(run_dir, "precision")),
                "recall":             _safe(_read_metric(run_dir, "recall")),
                "log_loss":           _safe(_read_metric(run_dir, "log_loss")),
                "mcc":                _safe(_read_metric(run_dir, "mcc")),
                "inference_ms":       _safe(_read_metric(run_dir, "inference_ms"), 3),
                "train_duration_sec": _safe(_read_metric(run_dir, "train_duration_sec"), 2),
                "ram_used_gb":        _safe(_read_metric(run_dir, "ram_used_gb"), 2),
                "ram_percent":        _safe(_read_metric(run_dir, "ram_percent"), 1),
                "cpu_percent":        _safe(_read_metric(run_dir, "cpu_percent"), 1),
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
