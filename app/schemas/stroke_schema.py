from pydantic import BaseModel

class StrokeRiskRequest(BaseModel):
    age: float
    gender: str          # "Nam", "Nữ", "Khác"
    height: float        # in cm
    weight: float        # in kg
    hypertension: bool   # True / False
    heart_disease: bool  # True / False
    glucose_level: float # in mg/dL
    smoking_status: str  # "Chưa từng hút", "Đã từng hút", "Thường xuyên hút"

class StrokeRiskResponse(BaseModel):
    bmi: float
    bmi_category: str
    risk_percentage: float
    risk_category: str
    recommendation: str
