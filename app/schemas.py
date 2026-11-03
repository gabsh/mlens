from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    model_name: str = Field(default="tfidf_lr")


class PredictResponse(BaseModel):
    label: str
    label_idx: int
    confidence: float
    probabilities: dict[str, float]
    model_name: str


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    model_name: str = Field(default="tfidf_lr")
    num_features: int = Field(default=10, ge=1, le=30)


class ExplainResponse(BaseModel):
    explanation: list[tuple[str, float]]
    model_name: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: list[str]
