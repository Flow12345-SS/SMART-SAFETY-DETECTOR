import os
import cv2
from typing import Dict, Any, List
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
import logging

logger = logging.getLogger(__name__)

class SafetyDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        self.load_model()

    def load_model(self):
        if not YOLO:
            logger.error("Ultralytics library not installed.")
            return

        if not os.path.exists(self.model_path):
            logger.warning(f"Model not found at {self.model_path}. Falling back to default yolov8n.pt.")
            
            # Vercel is read-only except for /tmp
            is_vercel = os.environ.get("VERCEL", False)
            fallback_path = '/tmp/yolov8n.pt' if is_vercel else 'yolov8n.pt'
            
            try:
                self.model = YOLO(fallback_path)
                logger.info(f"Loaded default {fallback_path} model")
            except Exception as e:
                logger.error(f"Error loading fallback model: {e}")
            return
        
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Loaded YOLO model from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

    def detect(self, frame) -> List[Dict[str, Any]]:
        if self.model is None:
            return []

        if frame is None or frame.size == 0:
            return []

        # Run inference (we use track mode if tracking is desired, but standard predict works as well)
        # Using predict for raw detections, we will apply tracking separately or use YOLO's built-in tracker
        results = self.model.track(frame, persist=True, conf=self.confidence_threshold, verbose=False)
        
        detections = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    
                    # tracking ID
                    track_id = int(box.id[0]) if box.id is not None else -1
                    
                    # Map labels if using default yolov8n
                    if label == 'cell phone':
                        label = 'mobile-phone'

                    detections.append({
                        "label": label,
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                        "tracking_id": track_id
                    })
        return detections

    def draw_detections(self, frame, detections: List[Dict[str, Any]]):
        """Helper to visualize detections manually if not using YOLO's plot()."""
        annotated = frame.copy()
        for d in detections:
            x1, y1, x2, y2 = map(int, d['bbox'])
            label = d['label']
            conf = d['confidence']
            track_id = d['tracking_id']
            
            text = f"{label} {conf:.2f} ID:{track_id}"
            
            color = (0, 255, 0)
            if label in ['fire', 'smoke', 'no-helmet', 'no-vest']:
                color = (0, 0, 255)
                
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, text, (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return annotated
