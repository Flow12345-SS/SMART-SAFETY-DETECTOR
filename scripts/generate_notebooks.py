import json
import os

os.makedirs('notebooks', exist_ok=True)

def create_nb(name, cells_data):
    cells = []
    for cell_type, source in cells_data:
        # splitlines(True) keeps the newline character
        source_lines = source.splitlines(True)
        cells.append({
            "cell_type": "markdown" if cell_type == "md" else "code",
            "metadata": {},
            "source": source_lines,
            **({"execution_count": None, "outputs": []} if cell_type == "code" else {})
        })
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    with open(f"notebooks/{name}", "w") as f:
        json.dump(nb, f, indent=2)

create_nb('01_dataset_exploration.ipynb', [
    ('md', '# 01 - Dataset Exploration\nExplore the workplace safety dataset structure, distributions, and visualize sample images and annotations.'),
    ('code', 'import os\nimport glob\nimport cv2\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport numpy as np\nimport yaml'),
    ('md', '## Configuration & Validation'),
    ('code', 'with open("../config/dataset.yaml", "r") as f:\n    config = yaml.safe_load(f)\n\nprint("Dataset configuration loaded:")\nprint(config)\n\nDATA_DIR = config["path"]'),
    ('md', '## Image and Label Counts'),
    ('code', 'train_images = glob.glob(os.path.join(DATA_DIR, config["train"], "*.jpg"))\nval_images = glob.glob(os.path.join(DATA_DIR, config["val"], "*.jpg"))\nprint(f"Total train images: {len(train_images)}")\nprint(f"Total validation images: {len(val_images)}")'),
    ('md', '## Bounding Box Analysis\nIterate over a few labels and visualize the bounding boxes.')
])

create_nb('02_dataset_preprocessing.ipynb', [
    ('md', '# 02 - Dataset Preprocessing\nValidate and preprocess images/labels. Clean up corrupt data or fix YOLO format issues.'),
    ('code', 'import os\nimport glob\nimport cv2'),
    ('md', '## Validation Function'),
    ('code', 'def validate_yolo_labels(label_dir, num_classes=8):\n    # Add implementation here to check for valid YOLO coordinates (0.0 to 1.0)\n    pass')
])

create_nb('03_yolo_training.ipynb', [
    ('md', '# 03 - YOLO Training\nTrain the object detection model on the prepared dataset using Ultralytics YOLOv8.'),
    ('code', '!pip install ultralytics'),
    ('code', 'from ultralytics import YOLO\nimport os'),
    ('md', '## Load Model'),
    ('code', 'model = YOLO("yolov8n.pt")  # Use nano model for faster training'),
    ('md', '## Train'),
    ('code', 'results = model.train(\n    data="../config/dataset.yaml",\n    epochs=50,\n    imgsz=640,\n    batch=16,\n    project="../outputs/training",\n    name="smart_safety_detector"\n)'),
    ('md', '## Save best weights'),
    ('code', 'import shutil\nbest_weight = os.path.join("../outputs/training", "smart_safety_detector", "weights", "best.pt")\nif os.path.exists(best_weight):\n    shutil.copy(best_weight, "../models/best.pt")\n    print("Copied best.pt to models/")')
])

create_nb('04_model_evaluation.ipynb', [
    ('md', '# 04 - Model Evaluation\nCalculate mAP, Precision, Recall and generate confusion matrices.'),
    ('code', 'from ultralytics import YOLO'),
    ('code', 'model = YOLO("../models/best.pt")'),
    ('md', '## Validate'),
    ('code', 'metrics = model.val(data="../config/dataset.yaml", project="../outputs/reports", name="validation_metrics")'),
    ('code', 'print(f"mAP50-95: {metrics.box.map}")\nprint(f"mAP50: {metrics.box.map50}")')
])

create_nb('05_inference_testing.ipynb', [
    ('md', '# 05 - Inference Testing\nTest the trained YOLO model on static images and a video file.'),
    ('code', 'import cv2\nimport matplotlib.pyplot as plt\nfrom ultralytics import YOLO'),
    ('code', 'model = YOLO("../models/best.pt")'),
    ('md', '## Predict on Image'),
    ('code', 'results = model.predict(source="../data/images/test/sample.jpg", conf=0.4)\nres_plotted = results[0].plot()\nplt.imshow(cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB))\nplt.show()')
])

create_nb('06_real_time_webcam.ipynb', [
    ('md', '# 06 - Real-time Webcam Inference\nUse cv2.VideoCapture to run real-time inference using the trained model.'),
    ('code', 'import cv2\nfrom ultralytics import YOLO'),
    ('code', 'model = YOLO("../models/best.pt")\ncap = cv2.VideoCapture(0)'),
    ('code', 'while cap.isOpened():\n    success, frame = cap.read()\n    if not success:\n        break\n    results = model(frame, conf=0.5)\n    annotated_frame = results[0].plot()\n    cv2.imshow("Smart Safety Detector", annotated_frame)\n    if cv2.waitKey(1) & 0xFF == ord("q"):\n        break\ncap.release()\ncv2.destroyAllWindows()')
])
