"""
Emotion Detector
Mendeteksi emosi dari cerita user menggunakan Gemini API
"""
from typing import Dict, Any, Optional
import logging

from core.llm.gemini_client import get_gemini_client
from core.knowledge.loader import get_knowledge_loader
from database.models.session import WellnessZoneEnum

logger = logging.getLogger(__name__)


class EmotionDetectionError(Exception):
    """Error saat deteksi emosi gagal"""
    pass


class EmotionDetector:
    """
    Detector untuk emosi user berdasarkan Feeling Wheel
    
    Menggunakan Gemini API Call #1 untuk:
    1. Mengidentifikasi primary, secondary, tertiary emotion
    2. Menentukan wellness zone
    3. Mengekstrak keywords
    """
    
    def __init__(self):
        """Initialize dengan gemini client dan knowledge loader"""
        self.gemini_client = get_gemini_client()
        self.knowledge_loader = get_knowledge_loader()
    
    async def detect(self, user_story: str) -> Dict[str, Any]:
        """
        Deteksi emosi dari cerita user
        
        Args:
            user_story: Cerita/curhat dari user
            
        Returns:
            Dict dengan:
            - primary_emotion: ID emosi primary
            - secondary_emotion: ID emosi secondary (optional)  
            - tertiary_emotion: ID emosi tertiary (optional)
            - keywords: List of keywords found
            - confidence: high/medium/low
            - wellness_zone: Zone enum value
            - reasoning: Explanation
        """
        try:
            # Get emotion wheel data
            emotion_wheel = self.knowledge_loader.get_emotion_wheel()
            
            # Call Gemini for detection
            result = await self.gemini_client.detect_emotion(
                user_story=user_story,
                emotion_wheel_data=emotion_wheel
            )
            
            # Validate and enrich result
            validated = self._validate_result(result)
            
            logger.info(
                f"Emotion detected: {validated['primary_emotion']} / "
                f"{validated.get('secondary_emotion')} / "
                f"{validated.get('tertiary_emotion')} "
                f"(confidence: {validated['confidence']})"
            )
            
            return validated
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {str(e)}")
            raise EmotionDetectionError(f"Failed to detect emotion: {str(e)}")
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and ensure result has all required fields
        
        Args:
            result: Raw result from Gemini
            
        Returns:
            Validated result with all required fields
        """
        validated = {
            "primary_emotion": result.get("primary_emotion", "sad"),
            "secondary_emotion": result.get("secondary_emotion"),
            "tertiary_emotion": result.get("tertiary_emotion"),
            "keywords": result.get("keywords", []),
            "confidence": result.get("confidence", "medium"),
            "wellness_zone": result.get("wellness_zone", "beradaptasi"),
            "reasoning": result.get("reasoning", "")
        }
        
        # Validate primary emotion exists in wheel
        primary = self.knowledge_loader.get_emotion_by_id(validated["primary_emotion"])
        if not primary:
            logger.warning(
                f"Invalid primary emotion: {validated['primary_emotion']}, defaulting to 'sad'"
            )
            validated["primary_emotion"] = "sad"
        
        # Validate secondary if present
        if validated["secondary_emotion"]:
            secondary = self.knowledge_loader.get_emotion_by_id(validated["secondary_emotion"])
            if not secondary:
                logger.warning(
                    f"Invalid secondary emotion: {validated['secondary_emotion']}, setting to None"
                )
                validated["secondary_emotion"] = None
        
        # Validate tertiary if present
        if validated["tertiary_emotion"]:
            tertiary = self.knowledge_loader.get_emotion_by_id(validated["tertiary_emotion"])
            if not tertiary:
                logger.warning(
                    f"Invalid tertiary emotion: {validated['tertiary_emotion']}, setting to None"
                )
                validated["tertiary_emotion"] = None
        
        # Validate wellness zone
        valid_zones = [z.value for z in WellnessZoneEnum]
        if validated["wellness_zone"] not in valid_zones:
            logger.warning(
                f"Invalid wellness zone: {validated['wellness_zone']}, defaulting to 'beradaptasi'"
            )
            validated["wellness_zone"] = "beradaptasi"
        
        # Validate confidence
        if validated["confidence"] not in ["high", "medium", "low"]:
            validated["confidence"] = "medium"
        
        return validated
    
    def get_emotion_label(
        self,
        emotion_id: str,
        language: str = "id"
    ) -> str:
        """
        Get human-readable label for emotion
        
        Args:
            emotion_id: ID of the emotion
            language: Language code (id/en)
            
        Returns:
            Label string
        """
        emotion = self.knowledge_loader.get_emotion_by_id(emotion_id)
        if emotion:
            labels = emotion.get("label", {})
            return labels.get(language, labels.get("en", emotion_id))
        return emotion_id
    
    def get_emotion_description(
        self,
        emotion_id: str,
        language: str = "id"
    ) -> str:
        """
        Get description for emotion
        
        Args:
            emotion_id: ID of the emotion
            language: Language code (id/en)
            
        Returns:
            Description string
        """
        emotion = self.knowledge_loader.get_emotion_by_id(emotion_id)
        if emotion:
            return emotion.get("description", "")
        return ""
    
    def get_emotion_summary(
        self,
        primary_id: str,
        secondary_id: Optional[str] = None,
        tertiary_id: Optional[str] = None,
        language: str = "id"
    ) -> str:
        """
        Get human-readable summary of detected emotion
        
        Args:
            primary_id: Primary emotion ID
            secondary_id: Secondary emotion ID (optional)
            tertiary_id: Tertiary emotion ID (optional)
            language: Language code
            
        Returns:
            Summary string like "Happy → Content → Satisfied"
        """
        parts = [self.get_emotion_label(primary_id, language)]
        
        if secondary_id:
            parts.append(self.get_emotion_label(secondary_id, language))
        
        if tertiary_id:
            parts.append(self.get_emotion_label(tertiary_id, language))
        
        return " → ".join(parts)


# Singleton instance
_emotion_detector: Optional[EmotionDetector] = None


def get_emotion_detector() -> EmotionDetector:
    """Get or create EmotionDetector singleton"""
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = EmotionDetector()
    return _emotion_detector
