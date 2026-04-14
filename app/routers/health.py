import os

import mlflow
from fastapi import APIRouter, Request

from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request):
    registry = request.app.state.registry
    return HealthResponse(
        status="ok",
        models_loaded=registry.available_models(),
    )


@router.get("/health/mlflow")
async def mlflow_health():
    try:
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
        mlflow.search_experiments()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}
