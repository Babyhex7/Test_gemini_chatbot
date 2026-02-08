"""
Emotion Log Model - Log deteksi emosi per session
"""
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database.base import Base


class EmotionLog(Base):
    """Model untuk menyimpan log deteksi emosi"""
    
    __tablename__ = "emotion_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    
    # Detected emotions (Feeling Wheel - 3 levels)
    primary_emotion = Column(String(50), nullable=False)    # happy, sad, angry, etc.
    secondary_emotion = Column(String(50), nullable=True)   # playful, content, lonely, etc.
    tertiary_emotion = Column(String(50), nullable=True)    # aroused, joyful, isolated, etc.
    
    # Emotion metadata
    emotion_keywords = Column(JSON, nullable=True)  # Keywords yang terdeteksi
    confidence_score = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Source text
    source_text = Column(Text, nullable=True)  # Teks yang dianalisis
    
    # Wellness zone
    wellness_zone = Column(String(50), nullable=True)
    
    # Detection method
    detection_phase = Column(String(50), nullable=True)  # initial, refined
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="emotion_logs")
    
    def __repr__(self):
        return f"<EmotionLog(id={self.id}, primary={self.primary_emotion})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "primary": self.primary_emotion,
            "secondary": self.secondary_emotion,
            "tertiary": self.tertiary_emotion,
            "keywords": self.emotion_keywords,
            "confidence": self.confidence_score,
            "wellness_zone": self.wellness_zone
        }
