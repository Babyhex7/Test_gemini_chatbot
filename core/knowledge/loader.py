"""
Knowledge Base Loader
Memuat dan cache data dari JSON knowledge base files
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Base path untuk knowledge base
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent.parent / "data" / "knowledge_base"


class KnowledgeLoader:
    """
    Loader untuk knowledge base JSON files
    
    Files yang dimuat:
    - wheel_of_emotion.json: Feeling Wheel data
    - reflection_questions.json: Pertanyaan refleksi & MC
    - coping_tips.json: Tips berdasarkan zona & emosi
    - wellness_zones.json: Definisi wellness zones
    """
    
    def __init__(self):
        """Initialize dengan cache kosong"""
        self._cache: Dict[str, Any] = {}
        self._loaded = False
    
    def load_all(self) -> None:
        """Load semua knowledge base files ke cache"""
        if self._loaded:
            return
        
        try:
            self._cache["emotion_wheel"] = self._load_json("wheel_of_emotion.json")
            self._cache["reflection_questions"] = self._load_json("reflection_questions.json")
            self._cache["coping_tips"] = self._load_json("coping_tips.json")
            self._cache["wellness_zones"] = self._load_json("wellness_zones.json")
            self._loaded = True
            logger.info("Knowledge base loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {str(e)}")
            raise
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load single JSON file"""
        file_path = KNOWLEDGE_BASE_PATH / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # ===== EMOTION WHEEL ACCESS =====
    
    def get_emotion_wheel(self) -> Dict[str, Any]:
        """Get complete emotion wheel data"""
        if not self._loaded:
            self.load_all()
        return self._cache.get("emotion_wheel", {})
    
    def get_primary_emotions(self) -> List[Dict[str, Any]]:
        """Get list of primary emotions"""
        wheel = self.get_emotion_wheel()
        return wheel.get("primary_emotions", [])
    
    def get_emotion_by_id(self, emotion_id: str) -> Optional[Dict[str, Any]]:
        """
        Find emotion by ID at any level
        
        Args:
            emotion_id: ID of the emotion (e.g., "happy", "playful", "aroused")
            
        Returns:
            Emotion dict or None
        """
        wheel = self.get_emotion_wheel()
        
        for primary in wheel.get("primary_emotions", []):
            if primary.get("id") == emotion_id:
                return {**primary, "level": "primary"}
            
            for secondary in primary.get("secondary_emotions", []):
                if secondary.get("id") == emotion_id:
                    return {**secondary, "level": "secondary", "parent": primary.get("id")}
                
                for tertiary in secondary.get("tertiary_emotions", []):
                    if tertiary.get("id") == emotion_id:
                        return {
                            **tertiary,
                            "level": "tertiary",
                            "parent": secondary.get("id"),
                            "grandparent": primary.get("id")
                        }
        
        return None
    
    def get_emotion_hierarchy(
        self,
        primary_id: str,
        secondary_id: Optional[str] = None,
        tertiary_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get full emotion hierarchy info"""
        result = {}
        
        primary = self.get_emotion_by_id(primary_id)
        if primary:
            result["primary"] = primary
        
        if secondary_id:
            secondary = self.get_emotion_by_id(secondary_id)
            if secondary:
                result["secondary"] = secondary
        
        if tertiary_id:
            tertiary = self.get_emotion_by_id(tertiary_id)
            if tertiary:
                result["tertiary"] = tertiary
        
        return result
    
    # ===== REFLECTION QUESTIONS ACCESS =====
    
    def get_reflection_questions(self) -> Dict[str, Any]:
        """Get complete reflection questions data"""
        if not self._loaded:
            self.load_all()
        return self._cache.get("reflection_questions", {})
    
    def get_questions_for_emotion(
        self,
        primary_id: str,
        secondary_id: Optional[str] = None,
        tertiary_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get questions for specific emotion hierarchy
        
        Returns dict with:
        - reflection_questions: List of 5 open-ended questions
        - mc_questions: List of 5 multiple choice questions
        """
        questions_data = self.get_reflection_questions()
        
        # Navigate to most specific level available
        primary_data = questions_data.get("primary_emotions", {}).get(primary_id, {})
        
        # Try tertiary first (most specific)
        if tertiary_id and secondary_id:
            secondary_data = primary_data.get("secondary_emotions", {}).get(secondary_id, {})
            tertiary_data = secondary_data.get("tertiary_emotions", {}).get(tertiary_id, {})
            if tertiary_data.get("reflection_questions"):
                return tertiary_data
        
        # Try secondary
        if secondary_id:
            secondary_data = primary_data.get("secondary_emotions", {}).get(secondary_id, {})
            if secondary_data.get("reflection_questions"):
                return secondary_data
        
        # Fall back to primary
        if primary_data.get("reflection_questions"):
            return primary_data
        
        # Return empty structure if nothing found
        return {
            "reflection_questions": [],
            "mc_questions": []
        }
    
    # ===== COPING TIPS ACCESS =====
    
    def get_coping_tips(self) -> Dict[str, Any]:
        """Get complete coping tips data"""
        if not self._loaded:
            self.load_all()
        return self._cache.get("coping_tips", {})
    
    def get_tips_by_zone(self, zone: str) -> List[Dict[str, Any]]:
        """Get tips for specific wellness zone"""
        tips_data = self.get_coping_tips()
        return tips_data.get("by_zone", {}).get(zone, [])
    
    def get_tips_by_emotion(self, emotion_type: str) -> List[Dict[str, Any]]:
        """Get tips for specific emotion type"""
        tips_data = self.get_coping_tips()
        return tips_data.get("by_emotion", {}).get(emotion_type, [])
    
    def get_tip_by_id(self, tip_id: str) -> Optional[Dict[str, Any]]:
        """Get specific tip by ID"""
        tips_data = self.get_coping_tips()
        
        # Search in by_zone
        for zone_tips in tips_data.get("by_zone", {}).values():
            for tip in zone_tips:
                if tip.get("id") == tip_id:
                    return tip
        
        # Search in by_emotion
        for emotion_tips in tips_data.get("by_emotion", {}).values():
            for tip in emotion_tips:
                if tip.get("id") == tip_id:
                    return tip
        
        return None
    
    # ===== WELLNESS ZONES ACCESS =====
    
    def get_wellness_zones(self) -> Dict[str, Any]:
        """Get complete wellness zones data"""
        if not self._loaded:
            self.load_all()
        return self._cache.get("wellness_zones", {})
    
    def get_zone_info(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get info for specific wellness zone"""
        zones_data = self.get_wellness_zones()
        return zones_data.get("zones", {}).get(zone_id)
    
    def get_zone_chatbot_action(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get chatbot action for specific zone"""
        zone_info = self.get_zone_info(zone_id)
        if zone_info:
            return zone_info.get("chatbot_action")
        return None


# Singleton instance
_knowledge_loader: Optional[KnowledgeLoader] = None


def get_knowledge_loader() -> KnowledgeLoader:
    """Get or create KnowledgeLoader singleton"""
    global _knowledge_loader
    if _knowledge_loader is None:
        _knowledge_loader = KnowledgeLoader()
        _knowledge_loader.load_all()
    return _knowledge_loader
