from fastapi import APIRouter, UploadFile, File
from app.services.face_service import analyze_face_symmetry

router = APIRouter()

@router.post("/predict-face")
async def predict_face_api(file: UploadFile = File(...)):
    print("DEBUG: Received request at /predict-face/")
    return await analyze_face_symmetry(file)