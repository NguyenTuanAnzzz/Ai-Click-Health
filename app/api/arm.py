from fastapi import APIRouter, UploadFile, File
from app.services.arm_service import predict_arm
from app.services.balance_service import predict_balance

router = APIRouter()

@router.post("/predict-arm")
async def predict_arm_api(file: UploadFile = File(...)):
    print("DEBUG: Received request at /predict-arm/")
    return await predict_arm(file)

@router.post("/predict-balance")
async def predict_balance_api(file: UploadFile = File(...)):
    print("DEBUG: Received request at /predict-balance/")
    return await predict_balance(file)
