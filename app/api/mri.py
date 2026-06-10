from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import numpy as np
import io
import os

# Biến global lưu model để load lười (lazy load)
mri_model_instance = None

def get_mri_model():
    global mri_model_instance
    if mri_model_instance is not None:
        return mri_model_instance
        
    try:
        os.environ["TF_USE_LEGACY_KERAS"] = "1"
        import tensorflow as tf
        
        class CustomDense(tf.keras.layers.Dense):
            def __init__(self, **kwargs):
                kwargs.pop('quantization_config', None)
                super().__init__(**kwargs)
                
        MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "stroke_mri_model.h5")
        if os.path.exists(MODEL_PATH):
            print(f"Đang nạp AI Model từ: {MODEL_PATH}")
            mri_model_instance = tf.keras.models.load_model(MODEL_PATH, custom_objects={'Dense': CustomDense}, compile=False)
            print("✅ Đã nạp thành công AI MRI!")
        else:
            print(f"⚠️ Chưa tìm thấy file model tại {MODEL_PATH}")
    except ImportError:
        print("⚠️ Cảnh báo: Thư viện 'tensorflow' chưa được cài đặt!")
        
    return mri_model_instance

router = APIRouter()

CLASSES = ["Não bình thường", "Nhồi máu não (Tắc mạch)", "Xuất huyết não (Vỡ mạch)"]

@router.post("/predict-mri")
async def analyze_mri_image(file: UploadFile = File(...)):
    model = get_mri_model()
    if model is None:
        raise HTTPException(status_code=500, detail="Mô hình AI chưa được nạp hoặc chưa cài đặt TensorFlow.")
        
    try:
        # 1. Đọc ảnh gửi lên
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 2. Tiền xử lý ảnh (Resize về 224x224 và chuẩn hóa 0-1)
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0) # [1, 224, 224, 3]
        
        # 3. Chạy model dự báo
        predictions = model.predict(img_array)[0]
        
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
