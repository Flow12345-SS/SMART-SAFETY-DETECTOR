from sqlalchemy.orm import Session
from src.database import models
from typing import List, Dict, Any
from datetime import datetime

def create_detection(db: Session, detection_data: Dict[str, Any], source: str, violation: bool = False, severity: str = None):
    bbox = detection_data.get('bbox', [0, 0, 0, 0])
    db_detection = models.Detection(
        label=detection_data['label'],
        confidence=detection_data['confidence'],
        x1=bbox[0],
        y1=bbox[1],
        x2=bbox[2],
        y2=bbox[3],
        tracking_id=detection_data.get('tracking_id', -1),
        source=source,
        violation=violation,
        severity=severity,
        timestamp=datetime.utcnow()
    )
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

def create_alert(db: Session, alert_data: Dict[str, Any]):
    db_alert = models.Alert(
        alert_type=alert_data['type'],
        severity=alert_data['severity'],
        message=alert_data['message'],
        status=alert_data.get('status', 'NEW'),
        timestamp=datetime.fromtimestamp(alert_data['timestamp'])
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_recent_detections(db: Session, limit: int = 100):
    return db.query(models.Detection).order_by(models.Detection.timestamp.desc()).limit(limit).all()

def get_recent_alerts(db: Session, limit: int = 50):
    return db.query(models.Alert).order_by(models.Alert.timestamp.desc()).limit(limit).all()

def get_statistics(db: Session):
    total_detections = db.query(models.Detection).count()
    total_alerts = db.query(models.Alert).count()
    
    # Violations by type
    violation_counts = {
        'NO_HELMET': db.query(models.Alert).filter(models.Alert.alert_type == 'NO_HELMET').count(),
        'NO_VEST': db.query(models.Alert).filter(models.Alert.alert_type == 'NO_VEST').count(),
        'FIRE': db.query(models.Alert).filter(models.Alert.alert_type == 'FIRE').count(),
        'SMOKE': db.query(models.Alert).filter(models.Alert.alert_type == 'SMOKE').count()
    }
    
    people_detected = db.query(models.Detection).filter(models.Detection.label == 'person').count()

    return {
        "total_detections": total_detections,
        "total_alerts": total_alerts,
        "people_detected": people_detected,
        "violations": violation_counts
    }
