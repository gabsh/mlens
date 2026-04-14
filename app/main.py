"""
FastAPI application entry point.
Models are loaded once at startup via the lifespan context.
"""
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import explain, health, metrics, predict  # noqa: E402

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(explain.router)
app.include_router(metrics.router)
