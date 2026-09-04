from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from src.database.db import Base
from datetime import datetime

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True)
    confidence = Column(Float)
    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)
    tracking_id = Column(Integer, nullable=True)
    source = Column(String)  # 'webcam', 'image', 'video'
    violation = Column(Boolean, default=False)
    severity = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, index=True)
    severity = Column(String)
    message = Column(String)
    status = Column(String, default="NEW")  # 'NEW', 'ACKNOWLEDGED', 'RESOLVED'
    timestamp = Column(DateTime, default=datetime.utcnow)
