from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class ArmFrame(BaseModel):
    t: float = 0
    lWristY: float
    rWristY: float
    lShoulderY: float
    rShoulderY: float
    shoulderWidth: float = Field(default=0.2, gt=0)


class BalanceFrame(BaseModel):
    t: float = 0
    shoulderMidX: float
    shoulderTilt: float
    cogOffset: float
    shoulderMidY: float = 0


class FaceFrame(BaseModel):
    t: float = 0
    deviationPct: float
    eyeDevPct: float = 0
    mouthDevPct: float = 0
    mouthCornerDevPct: float = 0
    mouthCenterOffsetPct: float = 0
    mouthSideBalancePct: float = 0
    cheekAsymmetryPct: float = 0
    mouthVerticalCenterPct: float = 0
    asymmetryScorePct: float = 0
    isAbnormal: bool = False


class AnalyzeArmRequest(BaseModel):
    frames: List[ArmFrame]
    min_frames: int = 45


class AnalyzeBalanceRequest(BaseModel):
    frames: List[BalanceFrame]
    min_frames: int = 45


class AnalyzeFaceRequest(BaseModel):
    frames: List[FaceFrame]
    min_frames: int = 30


class AnalyzeSpeechRequest(BaseModel):
    transcript: str
    duration_ms: int = 5000
    confidence: float = 1.0


class RealtimeAnalyzeResponse(BaseModel):
    success: bool
    realtime: bool = True
    error: Optional[str] = None
    label: Optional[str] = None
    message: Optional[str] = None
    riskLevel: Optional[Literal["low", "medium", "high"]] = None
    frameCount: Optional[int] = None
    extra: dict[str, Any] = Field(default_factory=dict)
