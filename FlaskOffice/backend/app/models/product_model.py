from app.database import db
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

class Detections(db.Model):
    __tablename__ = "detections"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String)
    filepath = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    inference_time_ms = db.Column(db.Float)
    num_detections = db.Column(db.Integer)
    classes_detected = db.Column(db.String)
    confidence_avg = db.Column(db.Float)
