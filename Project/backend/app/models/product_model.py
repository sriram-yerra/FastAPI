from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr    
from datetime import datetime
import os

class Detections(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    filepath: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    inference_time_ms: float
    num_detections: int
    classes_detected: str
    confidence_avg: float