import argparse
import os
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

def main():
    parser = argparse.ArgumentParser(description="Train Smart Safety Detector")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    if not YOLO:
        print("Ultralytics not installed. Run: pip install ultralytics")
        return

    model = YOLO("yolov8n.pt")
    print(f"Training for {args.epochs} epochs...")
    
    results = model.train(
        data="config/dataset.yaml",
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project="outputs/training",
        name="smart_safety_detector"
    )
    print("Training complete. Models saved in outputs/training/smart_safety_detector/")

if __name__ == "__main__":
    main()
