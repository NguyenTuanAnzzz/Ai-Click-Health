from app.services.temporal_math import clamp, detrend, linear_slope, risk_from_score, std


def analyze_balance_timeline(frames: list[dict], min_frames: int = 45) -> dict:
    if len(frames) < min_frames:
        return {
            "success": False,
            "error": "Không đủ dữ liệu thăng bằng.",
            "frameCount": len(frames),
        }

    sway_x = [f["shoulderMidX"] for f in frames]
    tilt = [f["shoulderTilt"] for f in frames]
    cog = [f["cogOffset"] for f in frames]
    shoulder_y = [f.get("shoulderMidY", 0) for f in frames]

    sway_pct = clamp(std(sway_x) * 1200, 0, 100)
    tilt_pct = clamp((sum(tilt) / len(tilt)) * 400, 0, 100)
    cog_pct = clamp(std(cog) * 800, 0, 100)
    body_drift = clamp(abs(linear_slope(detrend(shoulder_y))) * 600, 0, 100)
    movement_variance = clamp((sway_pct + cog_pct) / 2, 0, 100)

    stability_score = clamp(
        100 - sway_pct * 0.35 - tilt_pct * 0.3 - cog_pct * 0.2 - body_drift * 0.15,
        0,
        100,
    )
    left_right_balance = clamp(100 - tilt_pct, 0, 100)
    abnormal_motion_pct = clamp((sway_pct + movement_variance) / 2, 0, 100)

    risk_level = risk_from_score(stability_score)
    balance_issue = stability_score < 65 or sway_pct > 30 or tilt_pct > 25

    parts = []
    if sway_pct > 25:
        parts.append("Lắc người sang hai bên")
    if tilt_pct > 20:
        parts.append("Nghiêng vai đáng chú ý")
    if cog_pct > 22:
        parts.append("Trọng tâm không ổn định")
    if not parts:
        parts.append("Thăng bằng ổn định trong thời gian kiểm tra")

    return {
        "success": True,
        "realtime": True,
        "frameCount": len(frames),
        "stabilityScore": round(stability_score),
        "overallBalance": round(stability_score),
        "leftRightBalance": round(left_right_balance),
        "swayPct": round(sway_pct),
        "tiltPct": round(tilt_pct),
        "bodyDriftPct": round(body_drift),
        "movementVariance": round(movement_variance),
        "abnormalMotionPct": round(abnormal_motion_pct),
        "riskLevel": risk_level,
        "balance_issue": balance_issue,
        "label": "balance_issue" if balance_issue else "normal",
        "message": ". ".join(parts) + ".",
    }
