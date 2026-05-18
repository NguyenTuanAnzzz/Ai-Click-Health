from pathlib import Path

from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
PROCESSED_DIR = DATASET_DIR / "processed"
TRAIN_DIR = PROCESSED_DIR / "training_set"
TEST_DIR = PROCESSED_DIR / "test_set"
MODEL_OUTPUT = BASE_DIR.parents[1] / "models" / "face_model.h5"


train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
)

training_set = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(64, 64),
    batch_size=32,
    class_mode="binary",
)

test_datagen = ImageDataGenerator(rescale=1.0 / 255)
test_set = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(64, 64),
    batch_size=32,
    class_mode="binary",
)

cnn = tf.keras.models.Sequential()
cnn.add(
    tf.keras.layers.Conv2D(
        filters=32, kernel_size=3, activation="relu", input_shape=[64, 64, 3]
    )
)
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))
cnn.add(tf.keras.layers.Conv2D(filters=32, kernel_size=3, activation="relu"))
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))
cnn.add(tf.keras.layers.Flatten())
cnn.add(tf.keras.layers.Dense(units=128, activation="relu"))
cnn.add(tf.keras.layers.Dense(units=1, activation="sigmoid"))

cnn.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
cnn.fit(x=training_set, validation_data=test_set, epochs=25)

MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
cnn.save(MODEL_OUTPUT)

print("Class indices:", training_set.class_indices)
print(f"Saved model to: {MODEL_OUTPUT}")
