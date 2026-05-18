import io
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.python.solutions import pose as mp_pose
from PIL import Image

# mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

async def predict_arm(file):
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
            "arm_weakness": False,
            "confidence": 0.0,
            "message": "No person detected in the frame."
        }

    landmarks = results.pose_landmarks.landmark
    
    # Left arm: 11 (shoulder), 13 (elbow), 15 (wrist)
    # Right arm: 12 (shoulder), 14 (elbow), 16 (wrist)
    
    l_shoulder_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y
    r_shoulder_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
    l_wrist_y = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
    r_wrist_y = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y
    
    # In MediaPipe, Y increases downwards. Smaller Y means higher.
    # Check if arms are raised (wrists should be higher than shoulders or at least significantly up)
    # For a stroke test, we usually ask them to raise both arms.
    
    is_l_raised = l_wrist_y < l_shoulder_y
    is_r_raised = r_wrist_y < r_shoulder_y
    
    arm_weakness = False
    message = "Arms appear normal."
    
    if is_l_raised and is_r_raised:
        # Both raised, compare heights
        diff = abs(l_wrist_y - r_wrist_y)
        if diff > 0.1: # Threshold for significant difference
            arm_weakness = True
            message = "Significant height difference between arms detected."
    elif is_l_raised and not is_r_raised:
        arm_weakness = True
        message = "Right arm is not raised as high as the left arm."
    elif not is_l_raised and is_r_raised:
        arm_weakness = True
        message = "Left arm is not raised as high as the right arm."
    else:
        message = "Please raise both arms for the test."

    return {
        "label": "arm_weakness" if arm_weakness else "normal",
        "arm_weakness": arm_weakness,
        "l_wrist_y": float(l_wrist_y),
        "r_wrist_y": float(r_wrist_y),
        "message": message
    }
