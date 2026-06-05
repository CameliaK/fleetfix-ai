from pathlib import Path
import pandas as pd
import joblib
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Model lives at <project root>/ml/cost_model.joblib (3 levels up from this file)
MODEL_PATH = Path(__file__).resolve().parents[3] / "ml" / "cost_model.joblib"
model = joblib.load(MODEL_PATH)

class CostRequest(BaseModel):
    vehicle_type: str        # "truck" or "trailer"
    model_year: int
    labor_hours: float
    num_parts: int

@router.post("/cost")
def predict_cost(req: CostRequest):
    X = pd.DataFrame([req.model_dump()])   # the pipeline handles encoding
    estimate = float(model.predict(X)[0])
    return {"estimated_cost": round(estimate, 2)}