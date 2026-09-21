import logging

from fastapi import APIRouter, HTTPException, Request

from app.main import limiter
from app.prom_metrics import prediction_errors_total, predictions_total
from app.schemas import PredictRequest, PredictResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict/", response_model=PredictResponse)
@limiter.limit("20/minute")
async def predict(request: Request, body: PredictRequest):
    registry = request.app.state.registry

    if body.model_name not in registry.available_models():
        prediction_errors_total.labels(model_name="invalid", error_type="model_not_found").inc()
        raise HTTPException(
            status_code=404,
            detail=f"Model '{body.model_name}' not found. Available: {registry.available_models()}",
        )

    try:
        result = registry.predict(body.model_name, body.text)
    except Exception as e:
        logger.error("Predict error: %s", e)
        prediction_errors_total.labels(model_name=body.model_name, error_type="internal_error").inc()
        raise HTTPException(status_code=500, detail="Internal server error")

    predictions_total.labels(model_name=body.model_name, label=result["label"]).inc()
    return PredictResponse(**result, model_name=body.model_name)
