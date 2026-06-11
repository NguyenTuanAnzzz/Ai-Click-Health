from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import numpy as np
import io
import os

# Biến global lưu interpreter (TFLite)
mri_interpreter_instance = None
input_details = None
output_details = None

def get_mri_model():
    global mri_interpreter_instance, input_details, output_details
    if mri_interpreter_instance is not None:
        return mri_interpreter_instance, input_details, output_details
        
    try:
        import tflite_runtime.interpreter as tflite
        
        MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "stroke_mri_model.tflite")
        if os.path.exists(MODEL_PATH):
            print(f"Đang nạp AI Model từ: {MODEL_PATH}")
            mri_interpreter_instance = tflite.Interpreter(model_path=MODEL_PATH)
            mri_interpreter_instance.allocate_tensors()
            
            input_details = mri_interpreter_instance.get_input_details()
            output_details = mri_interpreter_instance.get_output_details()
            
            print("✅ Đã nạp thành công AI MRI (TFLite)!")
        else:
            print(f"⚠️ Chưa tìm thấy file model tại {MODEL_PATH}")
    except ImportError:
        print("⚠️ Cảnh báo: Thư viện 'tflite-runtime' chưa được cài đặt!")
        
    return mri_interpreter_instance, input_details, output_details

router = APIRouter()

CLASSES = ["Não bình thường", "Nhồi máu não (Tắc mạch)", "Xuất huyết não (Vỡ mạch)"]

@router.post("/predict-mri")
async def analyze_mri_image(file: UploadFile = File(...)):
    interpreter, input_dets, output_dets = get_mri_model()
    if interpreter is None:
        raise HTTPException(status_code=500, detail="Mô hình AI chưa được nạp hoặc chưa cài đặt tflite-runtime.")
        
    try:
        # 1. Đọc ảnh gửi lên
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 2. Tiền xử lý ảnh (Resize về 224x224 và chuẩn hóa 0-1)
        image = image.resize((224, 224))
        img_array = np.array(image, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0) # [1, 224, 224, 3]
        
        # 3. Chạy model dự báo (TFLite)
        interpreter.set_tensor(input_dets[0]['index'], img_array)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_dets[0]['index'])[0]
        
        # 4. Trích xuất kết quả
        max_index = np.argmax(predictions)
        confidence = float(predictions[max_index]) * 100
        
        # Format kết quả trả về Frontend
        return {
            "success": True,
            "diagnosis": CLASSES[max_index],
            "confidence_percent": round(confidence, 1),
            "raw_scores": {
                "normal": float(predictions[0]),
                "ischemic": float(predictions[1]),
                "hemorrhagic": float(predictions[2])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi xử lý ảnh: {str(e)}")
