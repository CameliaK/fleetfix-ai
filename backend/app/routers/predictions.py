from pathlib import Path
from functools import lru_cache
import os
import pandas as pd
import joblib
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/predictions", tags=["predictions"])

MODEL_PATH = Path(os.environ.get(
    "MODEL_PATH",
    Path(__file__).resolve().parents[3] / "ml" / "cost_model.joblib",
))

@lru_cache
def get_model():
    return joblib.load(MODEL_PATH)

class CostRequest(BaseModel):
    vehicle_type: str
    model_year: int
    labor_hours: float
    num_parts: int

@router.post("/cost")
def predict_cost(req: CostRequest):
    X = pd.DataFrame([req.model_dump()])
    estimate = float(get_model().predict(X)[0])
    return {"estimated_cost": round(estimate, 2)}