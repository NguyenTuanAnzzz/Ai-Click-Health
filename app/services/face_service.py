import io
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

async def analyze_face_symmetry(file):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"error": "Could not decode image"}

    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)

    if not results.multi_face_landmarks:
        return {
            "label": "no_face_detected",
            "deviation_percentage": 0,
            "is_abnormal": False,
            "message": "Không tìm thấy khuôn mặt trong ảnh."
        }

    landmarks = results.multi_face_landmarks[0].landmark
    
    # Key landmarks for symmetry (MediaPipe Face Mesh indices)
    # Eyes: Left (33, 133), Right (362, 263)
    # Mouth: Left corner (61), Right corner (291)
    
    # Calculate Eye Asymmetry (Vertical difference)
    l_eye_y = (landmarks[33].y + landmarks[133].y) / 2
    r_eye_y = (landmarks[362].y + landmarks[263].y) / 2
    eye_diff = abs(l_eye_y - r_eye_y)
    
    # Calculate Mouth Asymmetry (Vertical difference)
    l_mouth_y = landmarks[61].y
    r_mouth_y = landmarks[291].y
    mouth_diff = abs(l_mouth_y - r_mouth_y)
    
    # Normalize by face height (approximate as distance between forehead and chin)
    # Landmark 10: Top of forehead, Landmark 152: Bottom of chin
    face_height = abs(landmarks[10].y - landmarks[152].y)
    
    # Percentage deviation (Relative to face height)
    eye_dev_pct = (eye_diff / face_height) * 100
    mouth_dev_pct = (mouth_diff / face_height) * 100
    
    # Total deviation score
    total_deviation = max(eye_dev_pct, mouth_dev_pct)
    
    # Threshold for abnormality (e.g., 3-5% is often significant in medical imaging)
    is_abnormal = total_deviation > 3.5
    
    message = "Khuôn mặt cân đối."
    if is_abnormal:
        if mouth_dev_pct > 3.5:
            message = f"Phát hiện độ lệch miệng ({mouth_dev_pct:.1f}%). Có dấu hiệu liệt mặt."
        else:
            message = f"Phát hiện độ lệch mắt ({eye_dev_pct:.1f}%). Có dấu hiệu bất thường."

    return {
        "label": "face_droop" if is_abnormal else "normal",
        "deviation_percentage": round(total_deviation, 2),
        "eye_deviation": round(eye_dev_pct, 2),
        "mouth_deviation": round(mouth_dev_pct, 2),
        "is_abnormal": is_abnormal,
        "message": message
    }
