import io
import speech_recognition as sr
from pydub import AudioSegment
import os
import uuid

# Target phrase for the test
TARGET_PHRASE = "mẹ đi chợ mua cá"

async def predict_speech(file):
    # Generate unique filenames for this request to avoid collisions
    request_id = str(uuid.uuid4())
    temp_input = f"temp_in_{request_id}"
    temp_wav = f"temp_out_{request_id}.wav"
    
    try:
        # Read and save uploaded file
        contents = await file.read()
        with open(temp_input, "wb") as f:
            f.write(contents)
        
        # Convert to WAV
        # Browsers often send webm or ogg. SpeechRecognition needs WAV/AIFF/FLAC.
        try:
            audio = AudioSegment.from_file(temp_input)
            audio.export(temp_wav, format="wav")
        except Exception as e:
            print(f"Pydub conversion failed: {e}. Attempting direct rename.")
            # Fallback: hope it's already wav
            if os.path.exists(temp_wav): os.remove(temp_wav)
            os.rename(temp_input, temp_wav)

        recognizer = sr.Recognizer()
        
        # Ensure file exists before trying to open
        if not os.path.exists(temp_wav):
            return {"error": "Could not create audio file for analysis."}

        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            
            try:
                # Use Google Web Speech API
                text = recognizer.recognize_google(audio_data, language="vi-VN")
                text = text.strip().lower()
                
                if not text:
                    return {
                        "label": "speech_abnormal",
                        "speech_issue": True,
                        "recognized_text": "",
                        "message": "Không nghe rõ nội dung."
                    }

                is_correct = TARGET_PHRASE in text
                
                return {
                    "label": "normal" if is_correct else "speech_abnormal",
                    "speech_issue": not is_correct,
                    "recognized_text": text,
                    "target_phrase": TARGET_PHRASE,
                    "message": "Giọng nói bình thường." if is_correct else f"Bạn vừa nói: '{text}'. Giọng nói có dấu hiệu không chuẩn."
                }
                
            except sr.UnknownValueError:
                return {
                    "label": "speech_abnormal",
                    "speech_issue": True,
                    "recognized_text": "",
                    "message": "Không nhận diện được giọng nói."
                }
            except sr.RequestError as e:
                return {"error": f"Lỗi dịch vụ nhận diện: {e}"}
    
    except Exception as e:
        return {"error": f"Lỗi hệ thống: {str(e)}"}
        
    finally:
        # Cleanup temp files - wrap in try/except to ignore Windows lock errors during cleanup
        # as the unique names prevent collision anyway.
        for f in [temp_input, temp_wav]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass
