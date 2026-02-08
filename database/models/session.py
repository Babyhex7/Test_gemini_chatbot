"""
Chat Session Model - 4 Fase State Machine
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from database.base import Base


class PhaseEnum(str, enum.Enum):
    """Enum untuk 4 fase percakapan"""
    BERCERITA = "BERCERITA"           # Fase 1: User bercerita, Gemini deteksi emosi
    REFLEKSI_RINGAN = "REFLEKSI_RINGAN"  # Fase 2: 5 pertanyaan refleksi dari JSON
    NARASI_REFLEKTIF = "NARASI_REFLEKTIF"  # Fase 3: Generate narasi MHCM
    TIPS_CLOSING = "TIPS_CLOSING"      # Fase 4: Tips coping + closing
    SELESAI = "SELESAI"               # Session selesai


class WellnessZoneEnum(str, enum.Enum):
    """Enum untuk zona kesejahteraan"""
    SEIMBANG = "seimbang"
    BERADAPTASI = "beradaptasi"
    BUTUH_DUKUNGAN = "butuh_dukungan"
    PERLU_PERHATIAN = "perlu_perhatian"


class ChatSession(Base):
    """Model untuk menyimpan session chat dengan state machine"""
    
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # State Machine
    current_phase = Column(
        Enum(PhaseEnum),
        default=PhaseEnum.BERCERITA,
        nullable=False
    )
    
    # Fase 1 Results
    initial_story = Column(Text, nullable=True)
    detected_emotion_primary = Column(String(50), nullable=True)
    detected_emotion_secondary = Column(String(50), nullable=True)
    detected_emotion_tertiary = Column(String(50), nullable=True)
    emotion_confidence = Column(String(20), nullable=True)  # high, medium, low
    wellness_zone_initial = Column(Enum(WellnessZoneEnum), nullable=True)
    
    # Fase 2 Progress
    reflection_questions = Column(JSON, nullable=True)  # List of 5 questions
    reflection_answers = Column(JSON, nullable=True)    # List of 5 answers
    current_question_index = Column(Integer, default=0)
    
    # Fase 3 Results
    mhcm_narrative = Column(Text, nullable=True)
    wellness_zone_final = Column(Enum(WellnessZoneEnum), nullable=True)
    
    # Fase 4 Results
    tips_shown = Column(JSON, nullable=True)  # List of tips shown
    
    # Gemini API Tracking
    gemini_call_count = Column(Integer, default=0)  # Max: 2 per session
    
    # Metadata
    language = Column(String(10), default="id")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    emotion_logs = relationship("EmotionLog", back_populates="session", cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, phase={self.current_phase})>"
    
    def can_call_gemini(self) -> bool:
        """Check if session can still call Gemini API (max 2 calls)"""
        return self.gemini_call_count < 2
    
    def increment_gemini_call(self):
        """Increment Gemini call count"""
        self.gemini_call_count += 1
