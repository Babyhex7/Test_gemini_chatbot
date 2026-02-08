"""
Zone Mapper
Memetakan emosi ke wellness zone dan menentukan tindakan chatbot
"""
from typing import Dict, Any, Optional, List
import logging

from core.knowledge.loader import get_knowledge_loader
from database.models.session import WellnessZoneEnum

logger = logging.getLogger(__name__)


class ZoneMapper:
    """
    Mapper untuk wellness zones
    
    4 Zones (non-klinis):
    - seimbang (🟢): Flourishing, emosi positif dominan
    - beradaptasi (🟡): Moderate, ada tantangan tapi bisa diatasi
    - butuh_dukungan (🟠): Languishing, perlu perhatian ekstra
    - perlu_perhatian (🔴): Memerlukan eskalasi ke konselor
    """
    
    # Zone escalation rules
    ESCALATION_KEYWORDS = [
        "bunuh diri", "mati", "tidak ingin hidup", "mengakhiri",
        "menyakiti diri", "self harm", "cutting", "suicide",
        "tidak ada harapan", "putus asa total",
        "dipukuli", "dianiaya", "kekerasan", "abuse"
    ]
    
    CONCERN_KEYWORDS = [
        "sangat sedih", "depresi", "tidak bisa tidur", 
        "tidak nafsu makan", "terus menangis", "kosong",
        "tidak ada yang peduli", "sendirian", "dibully",
        "takut pulang", "tidak aman"
    ]
    
    def __init__(self):
        """Initialize dengan knowledge loader"""
        self.knowledge_loader = get_knowledge_loader()
    
    def get_zone_info(self, zone: WellnessZoneEnum) -> Dict[str, Any]:
        """
        Get complete info for a wellness zone
        
        Args:
            zone: WellnessZoneEnum value
            
        Returns:
            Zone info dict with labels, indicators, actions
        """
        return self.knowledge_loader.get_zone_info(zone.value) or {}
    
    def get_zone_label(self, zone: WellnessZoneEnum, language: str = "id") -> str:
        """Get human-readable label for zone"""
        zone_info = self.get_zone_info(zone)
        labels = zone_info.get("label", {})
        return labels.get(language, zone.value)
    
    def get_zone_emoji(self, zone: WellnessZoneEnum) -> str:
        """Get emoji for zone"""
        zone_info = self.get_zone_info(zone)
        return zone_info.get("emoji", "⚪")
    
    def get_chatbot_action(self, zone: WellnessZoneEnum) -> Dict[str, Any]:
        """
        Get recommended chatbot action for zone
        
        Returns:
            Dict with action details
        """
        return self.knowledge_loader.get_zone_chatbot_action(zone.value) or {}
    
    def check_escalation_needed(self, text: str) -> bool:
        """
        Check if text contains keywords that need immediate escalation
        
        Args:
            text: User message text
            
        Returns:
            True if escalation needed
        """
        text_lower = text.lower()
        
        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"Escalation keyword detected: {keyword}")
                return True
        
        return False
    
    def check_concern_level(self, text: str) -> bool:
        """
        Check if text contains concerning keywords
        
        Args:
            text: User message text
            
        Returns:
            True if concerns detected
        """
        text_lower = text.lower()
        
        concern_count = 0
        for keyword in self.CONCERN_KEYWORDS:
            if keyword in text_lower:
                concern_count += 1
        
        # 2+ concern keywords = elevated concern
        return concern_count >= 2
    
    def determine_zone(
        self,
        detected_zone: str,
        user_text: str,
        emotion_confidence: str = "medium"
    ) -> WellnessZoneEnum:
        """
        Determine final wellness zone with safety checks
        
        Args:
            detected_zone: Zone from Gemini detection
            user_text: User's message for keyword checking
            emotion_confidence: Confidence level from detection
            
        Returns:
            Final WellnessZoneEnum
        """
        # Check for immediate escalation
        if self.check_escalation_needed(user_text):
            logger.warning("Escalation needed - setting zone to perlu_perhatian")
            return WellnessZoneEnum.PERLU_PERHATIAN
        
        # Base zone from detection
        try:
            zone = WellnessZoneEnum(detected_zone)
        except ValueError:
            zone = WellnessZoneEnum.BERADAPTASI
        
        # Upgrade zone if concerning keywords detected
        if self.check_concern_level(user_text):
            if zone == WellnessZoneEnum.SEIMBANG:
                zone = WellnessZoneEnum.BERADAPTASI
            elif zone == WellnessZoneEnum.BERADAPTASI:
                zone = WellnessZoneEnum.BUTUH_DUKUNGAN
        
        # Low confidence with negative emotion = more cautious
        if emotion_confidence == "low" and zone in [
            WellnessZoneEnum.SEIMBANG,
            WellnessZoneEnum.BERADAPTASI
        ]:
            zone = WellnessZoneEnum.BERADAPTASI
        
        return zone
    
    def get_zone_response_guidelines(self, zone: WellnessZoneEnum) -> List[str]:
        """
        Get response guidelines for a zone
        
        Returns:
            List of guideline strings
        """
        action = self.get_chatbot_action(zone)
        guidelines = []
        
        if zone == WellnessZoneEnum.SEIMBANG:
            guidelines = [
                "Validasi perasaan positif user",
                "Celebrate wins, even small ones",
                "Encourage maintaining positive habits",
                "Light and supportive tone"
            ]
        
        elif zone == WellnessZoneEnum.BERADAPTASI:
            guidelines = [
                "Acknowledge challenges being faced",
                "Validate that struggling is normal",
                "Focus on coping strategies",
                "Encourage seeking support if needed",
                "Warm and understanding tone"
            ]
        
        elif zone == WellnessZoneEnum.BUTUH_DUKUNGAN:
            guidelines = [
                "Extra empathy and validation",
                "Avoid minimizing feelings",
                "Suggest speaking with trusted adult",
                "Provide grounding techniques",
                "Gentle reminder about support resources",
                "Very warm and supportive tone"
            ]
        
        elif zone == WellnessZoneEnum.PERLU_PERHATIAN:
            guidelines = [
                "PRIORITY: Ensure safety",
                "Validate without diving deep",
                "Strongly encourage speaking with counselor/adult",
                "Provide crisis resources if appropriate",
                "Keep response short and focused on safety",
                "Flag for human review"
            ]
        
        return guidelines
    
    def get_escalation_message(self, language: str = "id") -> str:
        """
        Get message for escalation situations
        
        Returns:
            Escalation message string
        """
        if language == "id":
            return """Aku mendengar bahwa kamu sedang melewati waktu yang sangat berat. 
Perasaanmu valid, dan aku ingin kamu tahu bahwa kamu tidak sendirian.

Aku sarankan untuk berbicara dengan orang dewasa yang kamu percaya - 
bisa guru BK, orang tua, atau konselor sekolah. 
Mereka bisa memberikan dukungan yang lebih mendalam.

Apakah ada orang dewasa di sekitarmu yang bisa kamu ajak bicara sekarang?"""
        else:
            return """I hear that you're going through a really tough time.
Your feelings are valid, and I want you to know you're not alone.

I suggest talking to a trusted adult -
it could be a school counselor, parent, or teacher.
They can provide more in-depth support.

Is there an adult near you that you can talk to now?"""


# Singleton instance
_zone_mapper: Optional[ZoneMapper] = None


def get_zone_mapper() -> ZoneMapper:
    """Get or create ZoneMapper singleton"""
    global _zone_mapper
    if _zone_mapper is None:
        _zone_mapper = ZoneMapper()
    return _zone_mapper
