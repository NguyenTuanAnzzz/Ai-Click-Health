from app.services.temporal_math import clamp, detrend, linear_slope, risk_from_score, std


def analyze_arm_timeline(frames: list[dict], min_frames: int = 45) -> dict:
    if len(frames) < min_frames:
        return {
            "success": False,
            "error": "Không đủ dữ liệu chuyển động.",
            "frameCount": len(frames),
        }

    raise_margin = 0  # Cho phép tay ngang vai (shoulder level) trở lên
    raised = 0
    height_diffs = []
    l_series = []
    r_series = []

    for f in frames:
        # Tay ở mức vai hoặc cao hơn: lWristY <= lShoulderY (Y nhỏ hơn = vị trí cao hơn)
        # Thêm 1% tolerance cho phép đo và góc camera
        if f["lWristY"] <= f["lShoulderY"] + 0.01 and f["rWristY"] <= f["rShoulderY"] + 0.01:
            raised += 1
        sw = f.get("shoulderWidth") or 0.2
        height_diffs.append(abs(f["lWristY"] - f["rWristY"]) / sw)
        l_series.append(f["lWristY"])
        r_series.append(f["rWristY"])

    n = len(frames)
    raise_pct = raised / n * 100
    l_drift = clamp(abs(linear_slope(l_series)) * 800, 0, 100)
    r_drift = clamp(abs(linear_slope(r_series)) * 800, 0, 100)
    arm_drift_pct = (l_drift + r_drift) / 2
    l_tremor = std(detrend(l_series))
    r_tremor = std(detrend(r_series))
    movement_variance = (l_tremor + r_tremor) / 2 * 1000

    stability_left = clamp(100 - l_drift * 0.55 - l_tremor * 180, 0, 100)
    stability_right = clamp(100 - r_drift * 0.55 - r_tremor * 180, 0, 100)
    left_right_balance = clamp(100 - (sum(height_diffs) / len(height_diffs)) * 100, 0, 100)
    composite = clamp(stability_left * 0.5 + stability_right * 0.5, 0, 100)
    composite = clamp(composite * 0.7 + left_right_balance * 0.3, 0, 100)
    abnormal_motion_pct = clamp((arm_drift_pct + movement_variance) / 2, 0, 100)

    raw_risk_level = risk_from_score(composite)
    arm_weakness = composite < 65 or stability_left < 65 or stability_right < 65 or raise_pct < 60
    risk_level = "medium" if arm_weakness and raw_risk_level == "low" else raw_risk_level

    parts = []
    if raise_pct < 60:
        parts.append("Hai tay chưa giơ đủ cao")
    if left_right_balance < 70:
        parts.append("Chênh lệch độ cao hai tay")
    if arm_drift_pct > 25:
        parts.append("Tay hạ dần khi giữ")
    if movement_variance > 18:
        parts.append("Dao động khi giữ tư thế")
    if not parts:
        parts.append("Tư thế giơ tay ổn định")

    return {
        "success": True,
        "realtime": True,
        "frameCount": n,
        "stabilityLeft": round(stability_left),
        "stabilityRight": round(stability_right),
        "overallBalance": round(composite),
        "leftRightBalance": round(left_right_balance),
        "armDriftPct": round(arm_drift_pct),
        "movementVariance": round(movement_variance),
        "abnormalMotionPct": round(abnormal_motion_pct),
        "raisePct": round(raise_pct),
        "riskLevel": risk_level,
        "armWeakness": arm_weakness,
        "arm_weakness": arm_weakness,
        "label": "arm_weakness" if arm_weakness else "normal",
        "message": ". ".join(parts) + ".",
    }
