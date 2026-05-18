from fastapi import APIRouter, Body
from pydantic import BaseModel

router = APIRouter()

class SpeechCheckRequest(BaseModel):
    text: str

TARGET_PHRASE = "mẹ đi chợ mua cá"

@router.post("/verify-speech")
async def verify_speech_api(request: SpeechCheckRequest):
    print(f"DEBUG: Received request at /verify-speech/ with text: {request.text}")
    recognized_text = request.text.lower().strip()
    
    # Kiểm tra xem câu mẫu có nằm trong văn bản nhận diện được không
    is_correct = TARGET_PHRASE in recognized_text
    
    message = "Giọng nói bình thường." if is_correct else f"Bạn vừa nói: '{recognized_text}'. Giọng nói có dấu hiệu không chuẩn."
    
    return {
        "label": "normal" if is_correct else "speech_abnormal",
        "speech_issue": not is_correct,
        "recognized_text": recognized_text,
        "target_phrase": TARGET_PHRASE,
        "message": message
    }
