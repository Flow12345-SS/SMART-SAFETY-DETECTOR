import argparse
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

def main():
    parser = argparse.ArgumentParser(description="Evaluate Smart Safety Detector")
    parser.add_argument("--weights", type=str, default="models/best.pt")
    args = parser.parse_args()

    if not YOLO:
        print("Ultralytics not installed. Run: pip install ultralytics")
        return

    model = YOLO(args.weights)
    print("Evaluating model...")
    
    metrics = model.val(
        data="config/dataset.yaml",
        project="outputs/reports",
        name="evaluation"
    )
    print(f"mAP50-95: {metrics.box.map}")
    print(f"mAP50: {metrics.box.map50}")

if __name__ == "__main__":
    main()
