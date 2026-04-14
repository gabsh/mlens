from fastapi import APIRouter, HTTPException, Request

from app.schemas import ExplainRequest, ExplainResponse

router = APIRouter(tags=["explanation"])


@router.post("/explain/", response_model=ExplainResponse)
async def explain(request: Request, body: ExplainRequest):
    registry = request.app.state.registry
    explainer = request.app.state.explainer

    if body.model_name not in registry.available_models():
        raise HTTPException(
            status_code=404,
            detail=f"Model '{body.model_name}' not found.",
        )

    try:
        result = explainer.explain(
            text=body.text,
            model_name=body.model_name,
            registry=registry,
            num_features=body.num_features,
        )
    except ValueError as e:
        # BERT not supported for LIME
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ExplainResponse(**result)
