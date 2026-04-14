from fastapi import APIRouter, HTTPException, Request

from app.schemas import PredictRequest, PredictResponse

router = APIRouter(tags=["prediction"])


@router.post("/predict/", response_model=PredictResponse)
async def predict(request: Request, body: PredictRequest):
    registry = request.app.state.registry

    if body.model_name not in registry.available_models():
        raise HTTPException(
            status_code=404,
            detail=f"Model '{body.model_name}' not found. Available: {registry.available_models()}",
        )

    try:
        result = registry.predict(body.model_name, body.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PredictResponse(**result, model_name=body.model_name)
