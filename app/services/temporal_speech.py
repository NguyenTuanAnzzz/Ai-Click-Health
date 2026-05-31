import re
import unicodedata

TARGET_PHRASE = "mẹ đi chợ mua cá"


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def _similarity(a: str, b: str) -> float:
    na, nb = _normalize(a), _normalize(b)
    if not na or not nb:
        return 0.0
    if nb in na or na in nb:
        return 100.0
    words_a = na.split()
    words_b = set(nb.split())
    if not words_a:
        return 0.0
    hit = sum(1 for w in words_a if w in words_b)
    return min(100.0, hit / len(words_a) * 100)


def analyze_speech(transcript: str, duration_ms: int = 5000, confidence: float = 1.0) -> dict:
    match_pct = _similarity(transcript, TARGET_PHRASE)
    duration_sec = max(duration_ms / 1000, 0.1)
    word_count = len(transcript.split())
    wpm = word_count / (duration_sec / 60) if duration_sec > 0 else 0
    speed_score = 100.0 if 80 <= wpm <= 200 else max(40.0, min(100.0, wpm))
    clarity = min(100.0, match_pct * 0.7 + speed_score * 0.15 + confidence * 100 * 0.15)

    speech_issue = match_pct < 70 or clarity < 65
    risk = "high" if clarity < 65 else "medium" if clarity < 80 else "low"

    return {
        "success": True,
        "realtime": True,
        "recognized_text": transcript,
        "target_phrase": TARGET_PHRASE,
        "matchPct": round(match_pct),
        "clarityScore": round(clarity),
        "overallBalance": round(clarity),
        "speech_issue": speech_issue,
        "label": "speech_abnormal" if speech_issue else "normal",
        "riskLevel": risk,
        "message": (
            f"Khớp câu mẫu {round(match_pct)}%. Có dấu hiệu nói không rõ."
            if speech_issue
            else "Giọng nói và nội dung đọc trong ngưỡng bình thường."
        ),
    }
