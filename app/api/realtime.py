from fastapi import APIRouter

from app.schemas.realtime import (
    AnalyzeArmRequest,
    AnalyzeBalanceRequest,
    AnalyzeFaceRequest,
    AnalyzeSpeechRequest,
)
from app.services.temporal_arm import analyze_arm_timeline
from app.services.temporal_balance import analyze_balance_timeline
from app.services.temporal_face import analyze_face_timeline
from app.services.temporal_speech import analyze_speech

router = APIRouter(prefix="/v1/realtime", tags=["realtime"])


@router.post("/analyze/arm")
async def analyze_arm(body: AnalyzeArmRequest):
    frames = [f.model_dump() for f in body.frames]
    return analyze_arm_timeline(frames, body.min_frames)


@router.post("/analyze/balance")
async def analyze_balance(body: AnalyzeBalanceRequest):
    frames = [f.model_dump() for f in body.frames]
    return analyze_balance_timeline(frames, body.min_frames)


@router.post("/analyze/face")
async def analyze_face(body: AnalyzeFaceRequest):
    frames = [f.model_dump() for f in body.frames]
    return analyze_face_timeline(frames, body.min_frames)


@router.post("/analyze/speech")
async def analyze_speech_endpoint(body: AnalyzeSpeechRequest):
    return analyze_speech(body.transcript, body.duration_ms, body.confidence)


@router.get("/health")
async def realtime_health():
    return {"status": "ok", "service": "befast-realtime"}
