import logging

from fastapi import APIRouter, HTTPException, Request

from app.main import limiter
from app.prom_metrics import explain_duration_seconds, explain_errors_total
from app.schemas import ExplainRequest, ExplainResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/explain/", response_model=ExplainResponse)
@limiter.limit("20/minute")
async def explain(request: Request, body: ExplainRequest):
    registry = request.app.state.registry
    explainer = request.app.state.explainer

    if body.model_name not in registry.available_models():
        explain_errors_total.labels(model_name="invalid", error_type="model_not_found").inc()
        raise HTTPException(
            status_code=404,
            detail=f"Model '{body.model_name}' not found.",
        )

    try:
        with explain_duration_seconds.labels(model_name=body.model_name).time():
            result = explainer.explain(
                text=body.text,
                model_name=body.model_name,
                registry=registry,
                num_features=body.num_features,
            )
    except ValueError as e:
        explain_errors_total.labels(model_name=body.model_name, error_type="invalid_input").inc()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Explain error: %s", e)
        explain_errors_total.labels(model_name=body.model_name, error_type="internal_error").inc()
        raise HTTPException(status_code=500, detail="Internal server error")

    return ExplainResponse(**result)
