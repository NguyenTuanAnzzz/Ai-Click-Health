import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import tensorflow as tf

MODEL_PATH = "stroke_mri_model.h5"

print("Đang nạp model...")
class CustomDense(tf.keras.layers.Dense):
    def __init__(self, **kwargs):
        kwargs.pop('quantization_config', None)
        super().__init__(**kwargs)

model = tf.keras.models.load_model(MODEL_PATH, custom_objects={'Dense': CustomDense}, compile=False)

print("Đang convert sang TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
# Optional: Tối ưu hoá dung lượng
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('stroke_mri_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("Done! stroke_mri_model.tflite created.")
