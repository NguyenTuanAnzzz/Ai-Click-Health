from app.services.temporal_math import clamp, risk_from_score


def analyze_face_timeline(frames: list[dict], min_frames: int = 30) -> dict:
    if len(frames) < min_frames:
        return {
            "success": False,
            "error": "Không đủ dữ liệu khuôn mặt.",
            "frameCount": len(frames),
        }

    deviations = [f["deviationPct"] for f in frames]
    mean_dev = sum(deviations) / len(deviations)
    max_dev = max(deviations)
    abnormal_frames = sum(1 for f in frames if f.get("isAbnormal") or f["deviationPct"] > 3.5)
    abnormal_pct = abnormal_frames / len(frames) * 100

    symmetry_score = clamp(100 - mean_dev * 8, 0, 100)
    stability_score = clamp(100 - (max_dev - mean_dev) * 5, 0, 100)
    composite = clamp(symmetry_score * 0.6 + stability_score * 0.4, 0, 100)

    risk_level = risk_from_score(composite)
    is_abnormal = max_dev > 3.5 or mean_dev > 2.8 or abnormal_pct > 35

    parts = []
    if max_dev > 3.5:
        parts.append(f"Độ lệch tối đa {max_dev:.1f}%")
    if abnormal_pct > 35:
        parts.append("Mất cân đối kéo dài")
    if not parts:
        parts.append("Khuôn mặt cân đối theo thời gian")

    return {
        "success": True,
        "realtime": True,
        "frameCount": len(frames),
        "deviation_percentage": round(max_dev, 1),
        "mean_deviation": round(mean_dev, 1),
        "symmetryScore": round(symmetry_score),
        "stabilityScore": round(stability_score),
        "overallBalance": round(composite),
        "abnormalMotionPct": round(abnormal_pct),
        "movementVariance": round(abnormal_pct),
        "riskLevel": risk_level,
        "is_abnormal": is_abnormal,
        "label": "face_droop" if is_abnormal else "normal",
        "message": ". ".join(parts) + ".",
    }
