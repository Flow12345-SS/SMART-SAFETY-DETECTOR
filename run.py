import argparse
import cv2
import yaml
from src.detection.detector import SafetyDetector
from src.safety.rule_engine import SafetyRuleEngine
from src.alerts.alert_manager import AlertManager

def main():
    parser = argparse.ArgumentParser(description="Run Smart Safety Detector")
    parser.add_argument("--source", type=str, required=True, choices=["image", "video", "webcam"], help="Source type")
    parser.add_argument("--path", type=str, help="Path to image or video file")
    args = parser.parse_args()

    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    detector = SafetyDetector(config['model']['path'], config['model']['confidence_threshold'])
    rule_engine = SafetyRuleEngine()
    alert_manager = AlertManager(config['alerts']['cooldown_seconds'])

    if args.source == "image":
        if not args.path:
            print("Error: --path is required for image source")
            return
        frame = cv2.imread(args.path)
        if frame is None:
            print(f"Error: Could not read image at {args.path}")
            return
        detections = detector.detect(frame)
        violations = rule_engine.evaluate(detections)
        alerts = alert_manager.process_violations(violations)
        
        annotated = detector.draw_detections(frame, detections)
        print(f"Detections: {detections}")
        print(f"Violations: {violations}")
        
        cv2.imshow("Result", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    elif args.source == "webcam":
        cap = cv2.VideoCapture(config['camera']['source'])
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            detections = detector.detect(frame)
            violations = rule_engine.evaluate(detections)
            alert_manager.process_violations(violations)
            
            annotated = detector.draw_detections(frame, detections)
            cv2.imshow("Smart Safety Detector", annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        
    elif args.source == "video":
        if not args.path:
            print("Error: --path is required for video source")
            return
        cap = cv2.VideoCapture(args.path)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            detections = detector.detect(frame)
            violations = rule_engine.evaluate(detections)
            alert_manager.process_violations(violations)
            
            annotated = detector.draw_detections(frame, detections)
            cv2.imshow("Smart Safety Detector - Video", annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
