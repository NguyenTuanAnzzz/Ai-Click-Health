from math import ceil

from app.services.temporal_math import clamp, risk_from_score


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0


def _percentile(values: list[float], p: float) -> float:
    sorted_values = sorted(v for v in values if isinstance(v, (int, float)))
    if not sorted_values:
        return 0
    idx = min(len(sorted_values) - 1, max(0, ceil(len(sorted_values) * p) - 1))
    return sorted_values[idx]


def _series(frames: list[dict], *keys: str) -> list[float]:
    values = []
    for frame in frames:
        picked = 0
        for idx, key in enumerate(keys):
            value = frame.get(key)
            if isinstance(value, (int, float)) and (value != 0 or idx == len(keys) - 1):
                picked = float(value)
                break
        values.append(picked)
    return values


def analyze_face_timeline(frames: list[dict], min_frames: int = 30) -> dict:
    if len(frames) < min_frames:
        return {
            "success": False,
            "error": "Không đủ dữ liệu khuôn mặt.",
            "frameCount": len(frames),
        }

    deviations = _series(frames, "asymmetryScorePct", "deviationPct")
    mouth_corner = _series(frames, "mouthCornerDevPct", "mouthDevPct", "deviationPct")
    mouth_center = _series(frames, "mouthCenterOffsetPct")
    mouth_side = _series(frames, "mouthSideBalancePct")
    eye_dev = _series(frames, "eyeDevPct")
    cheek_dev = _series(frames, "cheekAsymmetryPct")

    mean_dev = _average(deviations)
    median_dev = _percentile(deviations, 0.5)
    p90_dev = _percentile(deviations, 0.9)
    p95_dev = _percentile(deviations, 0.95)
    max_dev = max(deviations)
    p90_mouth = _percentile(mouth_corner, 0.9)
    median_mouth = _percentile(mouth_corner, 0.5)
    p90_center = _percentile(mouth_center, 0.9)
    median_center = _percentile(mouth_center, 0.5)
    p90_side = _percentile(mouth_side, 0.9)
    median_side = _percentile(mouth_side, 0.5)
    p90_eye = _percentile(eye_dev, 0.9)
    p90_cheek = _percentile(cheek_dev, 0.9)

    abnormal_frames = sum(
        1
        for frame in frames
        if frame.get("isAbnormal")
        or (frame.get("asymmetryScorePct", frame.get("deviationPct", 0)) > 4.8)
        or (frame.get("mouthCornerDevPct", frame.get("mouthDevPct", 0)) > 3.6)
        or (frame.get("mouthCenterOffsetPct", 0) > 5.0)
        or (frame.get("mouthSideBalancePct", 0) > 5.0)
    )
    abnormal_pct = abnormal_frames / len(frames) * 100

    composite_deviation = max(
        p90_dev,
        p95_dev * 0.9,
        median_dev * 1.25,
        p90_mouth * 1.1,
        p90_center * 0.95,
        p90_side * 0.9,
    )
    sustained_mouth_droop = median_mouth > 2.4 and p90_mouth > 3.4
    center_shift = median_center > 3.0 and p90_center > 4.2
    side_asymmetry = median_side > 3.0 and p90_side > 4.2
    peak_asymmetry = p95_dev > 5.2 and abnormal_pct > 20

    symmetry_score = clamp(100 - composite_deviation * 8 - abnormal_pct * 0.18, 0, 100)
    stability_score = clamp(100 - clamp(p95_dev - median_dev, 0, 10) * 5 - abnormal_pct * 0.08, 0, 100)
    movement_variance = clamp(abnormal_pct, 0, 100)
    composite = clamp(symmetry_score * 0.6 + stability_score * 0.4, 0, 100)

    is_abnormal = (
        sustained_mouth_droop
        or center_shift
        or side_asymmetry
        or peak_asymmetry
        or abnormal_pct > 45
    )
    raw_risk_level = risk_from_score(composite)
    risk_level = "medium" if is_abnormal and raw_risk_level == "low" else raw_risk_level

    parts = []
    if sustained_mouth_droop:
        parts.append(f"Độ lệch khóe miệng {p90_mouth:.1f}%")
    if center_shift:
        parts.append(f"Tâm miệng lệch khỏi trục mặt {p90_center:.1f}%")
    if side_asymmetry:
        parts.append(f"Vùng miệng/má mất cân đối {p90_side:.1f}%")
    if peak_asymmetry:
        parts.append(f"Bất đối xứng khuôn mặt {p95_dev:.1f}%")
    if abnormal_pct > 45:
        parts.append(f"Bất đối xứng kéo dài {round(abnormal_pct)}% thời lượng")
    if not parts:
        parts.append("Khuôn mặt cân đối theo thời gian")

    return {
        "success": True,
        "realtime": True,
        "frameCount": len(frames),
        "deviation_percentage": round(composite_deviation, 1),
        "max_deviation": round(max_dev, 1),
        "mean_deviation": round(mean_dev, 1),
        "median_deviation": round(median_dev, 1),
        "mouth_corner_deviation": round(p90_mouth, 1),
        "mouth_center_offset": round(p90_center, 1),
        "mouth_side_balance": round(p90_side, 1),
        "eye_deviation": round(p90_eye, 1),
        "cheek_asymmetry": round(p90_cheek, 1),
        "symmetryScore": round(symmetry_score),
        "stabilityScore": round(stability_score),
        "overallBalance": round(composite),
        "abnormalMotionPct": round(abnormal_pct),
        "movementVariance": round(movement_variance),
        "riskLevel": risk_level,
        "is_abnormal": is_abnormal,
        "label": "face_droop" if is_abnormal else "normal",
        "message": ". ".join(parts) + ".",
    }
