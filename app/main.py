"""
FastAPI application entry point.
Models are loaded once at startup via the lifespan context.
"""
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

limiter = Limiter(key_func=get_remote_address)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    from src.nlp_classifier.explainer import TextExplainer
    from src.nlp_classifier.inference import ModelRegistry

    model_dir = os.getenv("MODEL_DIR", "./models")
    logger.info(f"Loading models from {model_dir}...")
    app.state.registry = ModelRegistry(model_dir=model_dir)
    app.state.explainer = TextExplainer()
    logger.info(f"Ready. Models loaded: {app.state.registry.available_models()}")
    yield
    # --- SHUTDOWN ---
    logger.info("Shutting down.")


app = FastAPI(
    title="NLP Binary Classifier API",
    description="Multi-embedding × multi-classifier comparison on IMDB sentiment.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mlens.fr", "https://www.mlens.fr"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

from app.routers import explain, health, metrics, predict, roc  # noqa: E402

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(explain.router)
app.include_router(metrics.router)
app.include_router(roc.router)
