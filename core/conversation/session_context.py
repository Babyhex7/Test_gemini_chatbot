"""
Session Context
In-memory context untuk sesi chat aktif
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

from database.models.session import PhaseEnum, WellnessZoneEnum


@dataclass
class SessionContext:
    """
    In-memory context untuk sesi chat
    
    Menyimpan state sementara yang belum di-persist ke database
    """
    # Session info
    session_id: int
    user_id: int
    
    # Phase state
    current_phase: PhaseEnum = PhaseEnum.BERCERITA
    
    # Fase 1: BERCERITA
    user_story: str = ""
    
    # Emotion detection result
    detected_emotion: Dict[str, Any] = field(default_factory=dict)
    primary_emotion: Optional[str] = None
    secondary_emotion: Optional[str] = None
    tertiary_emotion: Optional[str] = None
    emotion_keywords: List[str] = field(default_factory=list)
    emotion_confidence: str = "medium"
    
    # Wellness zone
    wellness_zone: WellnessZoneEnum = WellnessZoneEnum.BERADAPTASI
    
    # Fase 2: REFLEKSI_RINGAN
    reflection_questions: List[Dict[str, Any]] = field(default_factory=list)
    reflection_answers: List[Dict[str, str]] = field(default_factory=list)
    current_question_index: int = 0
    
    # Fase 3: NARASI_REFLEKTIF
    mhcm_narrative: str = ""
    narrative_insights: List[str] = field(default_factory=list)
    
    # Fase 4: TIPS_CLOSING
    selected_tips: List[Dict[str, Any]] = field(default_factory=list)
    
    # Gemini API tracking
    gemini_call_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def can_call_gemini(self) -> bool:
        """Check if we can still call Gemini API (max 2)"""
        return self.gemini_call_count < 2
    
    def increment_gemini_call(self) -> None:
        """Increment Gemini call counter"""
        self.gemini_call_count += 1
    
    def set_detected_emotion(self, emotion_data: Dict[str, Any]) -> None:
        """Set detected emotion from Gemini response"""
        self.detected_emotion = emotion_data
        self.primary_emotion = emotion_data.get("primary_emotion")
        self.secondary_emotion = emotion_data.get("secondary_emotion")
        self.tertiary_emotion = emotion_data.get("tertiary_emotion")
        self.emotion_keywords = emotion_data.get("keywords", [])
        self.emotion_confidence = emotion_data.get("confidence", "medium")
        
        # Set wellness zone
        zone_str = emotion_data.get("wellness_zone", "beradaptasi")
        try:
            self.wellness_zone = WellnessZoneEnum(zone_str)
        except ValueError:
            self.wellness_zone = WellnessZoneEnum.BERADAPTASI
    
    def add_reflection_answer(self, question: str, answer: str) -> None:
        """Add a reflection Q&A pair"""
        self.reflection_answers.append({
            "question": question,
            "answer": answer
        })
        self.current_question_index += 1
    
    def is_reflection_complete(self) -> bool:
        """Check if all 5 reflection questions are answered"""
        return len(self.reflection_answers) >= 5
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get current reflection question"""
        if self.current_question_index < len(self.reflection_questions):
            return self.reflection_questions[self.current_question_index]
        return None
    
    def set_narrative(self, narrative_data: Dict[str, Any]) -> None:
        """Set narrative from Gemini response"""
        self.mhcm_narrative = narrative_data.get("narrative", "")
        self.narrative_insights = narrative_data.get("insights", [])
        
        # Update wellness zone if present
        zone_str = narrative_data.get("wellness_zone")
        if zone_str:
            try:
                self.wellness_zone = WellnessZoneEnum(zone_str)
            except ValueError:
                pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for persistence"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_phase": self.current_phase.value,
            "user_story": self.user_story,
            "detected_emotion": self.detected_emotion,
            "primary_emotion": self.primary_emotion,
            "secondary_emotion": self.secondary_emotion,
            "tertiary_emotion": self.tertiary_emotion,
            "emotion_keywords": self.emotion_keywords,
            "emotion_confidence": self.emotion_confidence,
            "wellness_zone": self.wellness_zone.value,
            "reflection_questions": self.reflection_questions,
            "reflection_answers": self.reflection_answers,
            "current_question_index": self.current_question_index,
            "mhcm_narrative": self.mhcm_narrative,
            "narrative_insights": self.narrative_insights,
            "selected_tips": self.selected_tips,
            "gemini_call_count": self.gemini_call_count,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        """Create context from dictionary"""
        context = cls(
            session_id=data["session_id"],
            user_id=data["user_id"]
        )
        context.current_phase = PhaseEnum(data.get("current_phase", "bercerita"))
        context.user_story = data.get("user_story", "")
        context.detected_emotion = data.get("detected_emotion", {})
        context.primary_emotion = data.get("primary_emotion")
        context.secondary_emotion = data.get("secondary_emotion")
        context.tertiary_emotion = data.get("tertiary_emotion")
        context.emotion_keywords = data.get("emotion_keywords", [])
        context.emotion_confidence = data.get("emotion_confidence", "medium")
        context.wellness_zone = WellnessZoneEnum(data.get("wellness_zone", "beradaptasi"))
        context.reflection_questions = data.get("reflection_questions", [])
        context.reflection_answers = data.get("reflection_answers", [])
        context.current_question_index = data.get("current_question_index", 0)
        context.mhcm_narrative = data.get("mhcm_narrative", "")
        context.narrative_insights = data.get("narrative_insights", [])
        context.selected_tips = data.get("selected_tips", [])
        context.gemini_call_count = data.get("gemini_call_count", 0)
        
        return context
