from fastapi import APIRouter
from app.schemas.stroke_schema import StrokeRiskRequest, StrokeRiskResponse
from app.services.stroke_service import calculate_stroke_risk

router = APIRouter()

@router.post("/predict-stroke", response_model=StrokeRiskResponse)
async def predict_stroke_api(data: StrokeRiskRequest):
    print(f"DEBUG: Received request at /predict-stroke/ with data: {data}")
    return calculate_stroke_risk(data)
