import io
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.python.solutions import pose as mp_pose

# mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

async def predict_balance(file):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"error": "Could not decode image"}

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if not results.pose_landmarks:
        return {
            "label": "no_pose_detected",
            "balance_issue": False,
            "confidence": 0.0,
            "message": "No person detected in the frame."
        }

    landmarks = results.pose_landmarks.landmark
    
    # Check shoulder alignment
    l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    
    # Calculate angle of shoulders
    shoulder_dy = l_shoulder.y - r_shoulder.y
    shoulder_dx = l_shoulder.x - r_shoulder.x
    angle = np.degrees(np.arctan2(shoulder_dy, shoulder_dx))
    
    # Normalized angle (around 180 or 0 depending on coordinates)
    # Actually arctan2(dy, dx) for horizontal line should be near 0 or 180.
    # Let's check absolute difference in Y
    shoulder_diff = abs(l_shoulder.y - r_shoulder.y)
    
    # Check vertical alignment (nose to midpoint of hips)
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    hip_mid_x = (l_hip.x + r_hip.x) / 2
    
    tilt = abs(nose.x - hip_mid_x)
    
    balance_issue = False
    message = "Balance appears normal."
    
    if shoulder_diff > 0.05: # Threshold for shoulder tilt
        balance_issue = True
        message = "Significant shoulder tilt detected."
    elif tilt > 0.1: # Threshold for body tilt
        balance_issue = True
        message = "Significant body tilt detected."

    return {
        "label": "balance_issue" if balance_issue else "normal",
        "balance_issue": balance_issue,
        "shoulder_diff": float(shoulder_diff),
        "body_tilt": float(tilt),
        "message": message
    }
