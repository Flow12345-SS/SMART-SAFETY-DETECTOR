from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.database import models, crud
from src.database.db import engine, get_db
from src.detection.detector import SafetyDetector
from src.safety.rule_engine import SafetyRuleEngine
from src.alerts.alert_manager import AlertManager
import cv2
import numpy as np
import yaml
import time
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize Core AI Components
detector = SafetyDetector(
    model_path=config['model']['path'],
    confidence_threshold=config['model']['confidence_threshold']
)
rule_engine = SafetyRuleEngine()
alert_manager = AlertManager(cooldown_seconds=config['alerts']['cooldown_seconds'])

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": detector.model is not None}

@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    return crud.get_statistics(db)

@router.get("/detections/recent")
def get_recent_detections(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_recent_detections(db, limit)

@router.get("/alerts/recent")
def get_recent_alerts(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_recent_alerts(db, limit)

@router.post("/detect-image")
async def detect_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")

    try:
        start_time = time.time()
        
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image data.")

        # Detect
        detections = detector.detect(img)
        
        # Rules
        violations = rule_engine.evaluate(detections)
        
        # Alerts
        new_alerts = alert_manager.process_violations(violations)

        # Save to DB
        violation_types = [v['type'] for v in violations]
        
        for d in detections:
            # Simple assumption: if a violation relates to this label/bbox, mark it.
            is_violating = any(v['type'] in ['FIRE', 'SMOKE', 'MOBILE_PHONE'] for v in violations)
            crud.create_detection(db, d, source="image", violation=is_violating)
            
        for a in new_alerts:
            crud.create_alert(db, a)

        # Optional: Save annotated image (skipped to save space, but could return base64)
        
        processing_time = time.time() - start_time

        return {
            "success": True,
            "detections": detections,
            "violations": violations,
            "new_alerts": new_alerts,
            "processing_time": processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
