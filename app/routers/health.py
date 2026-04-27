from fastapi import APIRouter, Request

from app.routers.metrics import MLRUNS_DIR
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
    return {"status": "ok" if MLRUNS_DIR.exists() else "error"}
