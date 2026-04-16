import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["roc"])


@router.get("/roc")
async def get_roc_curves():
    path = Path(os.getenv("MODEL_DIR", "./models")) / "roc_curves.json"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="roc_curves.json not found — run: python run.py evaluate",
        )
    return json.loads(path.read_text())
