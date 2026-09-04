import os
import cv2
import numpy as np
from typing import Dict, Any, List
import logging

try:
    import onnxruntime as ort
except ImportError:
    ort = None

logger = logging.getLogger(__name__)

# YOLOv8 COCO classes
CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]

class SafetyDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        # We enforce .onnx extension
        if model_path.endswith('.pt'):
            self.model_path = model_path.replace('.pt', '.onnx')
        else:
            self.model_path = model_path
            
        self.confidence_threshold = confidence_threshold
        self.session = None
        self.input_name = None
        
        self.load_model()

    def load_model(self):
        if not ort:
            logger.error("ONNXRuntime library not installed.")
            return

        if not os.path.exists(self.model_path):
            logger.warning(f"Model not found at {self.model_path}. Trying default.")
            self.model_path = 'yolov8n.onnx'
            
        if not os.path.exists(self.model_path):
            logger.error(f"Failed to find {self.model_path}. Please ensure the ONNX model is present.")
            return

        try:
            self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])
            self.input_name = self.session.get_inputs()[0].name
            logger.info(f"Loaded ONNX model from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")

    def detect(self, frame) -> List[Dict[str, Any]]:
        if self.session is None:
            return []

        if frame is None or frame.size == 0:
            return []

        # Preprocess
        img_h, img_w = frame.shape[:2]
        
        # YOLOv8 default size
        input_size = (640, 640)
        
        # Resize without padding (simple resize for stateless api)
        # Note: letterbox padding is more accurate but simple resize works fine for general use
        resized = cv2.resize(frame, input_size)
        
        # BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Transpose to CHW and normalize
        input_tensor = rgb.transpose(2, 0, 1).astype(np.float32) / 255.0
        input_tensor = np.expand_dims(input_tensor, axis=0)

        # Inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # Postprocess
        # outputs[0] shape: (1, 84, 8400)
        predictions = outputs[0][0] # shape (84, 8400)
        
        # Transpose to (8400, 84)
        predictions = predictions.T
        
        boxes = predictions[:, :4]
        scores = predictions[:, 4:]
        
        # Get max score and class id
        class_ids = np.argmax(scores, axis=1)
        confidences = np.max(scores, axis=1)
        
        # Filter by threshold
        mask = confidences > self.confidence_threshold
        boxes = boxes[mask]
        class_ids = class_ids[mask]
        confidences = confidences[mask]
        
        # Rescale boxes back to original image
        x_factor = img_w / input_size[0]
        y_factor = img_h / input_size[1]
        
        detections = []
        
        if len(boxes) == 0:
            return detections
            
        # Convert cx, cy, w, h to x1, y1, x2, y2
        cx, cy, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        x1 = (cx - w / 2) * x_factor
        y1 = (cy - h / 2) * y_factor
        x2 = (cx + w / 2) * x_factor
        y2 = (cy + h / 2) * y_factor
        
        # NMS
        boxes_cv2 = np.column_stack((x1, y1, x2 - x1, y2 - y1)).tolist() # x, y, w, h
        indices = cv2.dnn.NMSBoxes(boxes_cv2, confidences.tolist(), self.confidence_threshold, 0.45)
        
        if len(indices) > 0:
            for i in indices.flatten():
                label = CLASSES[class_ids[i]]
                if label == 'cell phone':
                    label = 'mobile-phone'
                    
                detections.append({
                    "label": label,
                    "confidence": float(confidences[i]),
                    "bbox": [float(x1[i]), float(y1[i]), float(x2[i]), float(y2[i])],
                    "tracking_id": -1 # Tracking removed for Vercel
                })

        return detections

    def draw_detections(self, frame, detections: List[Dict[str, Any]]):
        annotated = frame.copy()
        for d in detections:
            x1, y1, x2, y2 = map(int, d['bbox'])
            label = d['label']
            conf = d['confidence']
            track_id = d['tracking_id']
            
            text = f"{label} {conf:.2f}"
            if track_id != -1:
                text += f" ID:{track_id}"
            
            color = (0, 255, 0)
            if label in ['fire', 'smoke', 'no-helmet', 'no-vest']:
                color = (0, 0, 255)
                
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, text, (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return annotated
