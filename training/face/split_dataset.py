import random
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
RAW_DIR = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"
TRAIN_DIR = PROCESSED_DIR / "training_set"
TEST_DIR = PROCESSED_DIR / "test_set"
CLASSES = ["normal", "face_droop"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
TEST_RATIO = 0.2
SEED = 42


def list_images(folder: Path):
    return [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def reset_output_dirs():
    for root in (TRAIN_DIR, TEST_DIR):
        for class_name in CLASSES:
            class_dir = root / class_name
            if class_dir.exists():
                for item in class_dir.iterdir():
                    if item.is_file():
                        item.unlink()
            else:
                class_dir.mkdir(parents=True, exist_ok=True)


def split_class(class_name: str):
    source_dir = RAW_DIR / class_name
    images = list_images(source_dir)

    if not images:
        print(f"No images found in {source_dir}")
        return

    random.shuffle(images)
    test_count = max(1, int(len(images) * TEST_RATIO)) if len(images) > 1 else 0
    test_images = images[:test_count]
    train_images = images[test_count:]

    for image_path in train_images:
        shutil.copy2(image_path, TRAIN_DIR / class_name / image_path.name)

    for image_path in test_images:
        shutil.copy2(image_path, TEST_DIR / class_name / image_path.name)

    print(
        f"{class_name}: total={len(images)}, train={len(train_images)}, test={len(test_images)}"
    )


def main():
    random.seed(SEED)
    reset_output_dirs()

    for class_name in CLASSES:
        split_class(class_name)

    print("Dataset split completed.")
    print(f"Training set: {TRAIN_DIR}")
    print(f"Test set: {TEST_DIR}")


if __name__ == "__main__":
    main()
