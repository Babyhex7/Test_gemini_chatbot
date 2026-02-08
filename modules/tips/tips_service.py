"""
Tips Service
Mengelola tips coping berdasarkan wellness zone dan emosi
"""
from typing import Dict, Any, List, Optional
import random
import logging

from core.knowledge.loader import get_knowledge_loader
from core.conversation.session_context import SessionContext
from database.models.session import WellnessZoneEnum

logger = logging.getLogger(__name__)


class TipsService:
    """
    Service untuk tips coping
    
    Memilih tips berdasarkan:
    1. Wellness zone (priority)
    2. Emosi yang terdeteksi
    3. Konteks sesi
    """
    
    def __init__(self):
        """Initialize dengan knowledge loader"""
        self.loader = get_knowledge_loader()
    
    def get_tips_for_session(
        self,
        context: SessionContext,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get tips berdasarkan session context
        
        Args:
            context: Session context
            count: Jumlah tips yang diinginkan
            
        Returns:
            List of tip dicts
        """
        zone = context.wellness_zone
        emotion = context.primary_emotion
        
        # Get tips by zone (primary)
        zone_tips = self.loader.get_tips_by_zone(zone.value)
        
        # Get tips by emotion (secondary)
        emotion_tips = []
        if emotion:
            emotion_tips = self.loader.get_tips_by_emotion(emotion)
        
        # Combine and deduplicate
        all_tips = self._merge_tips(zone_tips, emotion_tips)
        
        # Select tips
        selected = self._select_tips(all_tips, count)
        
        # Store in context
        context.selected_tips = selected
        
        logger.info(
            f"Selected {len(selected)} tips for session {context.session_id} "
            f"(zone: {zone.value}, emotion: {emotion})"
        )
        
        return selected
    
    def _merge_tips(
        self,
        zone_tips: List[Dict[str, Any]],
        emotion_tips: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge tips from different sources, avoiding duplicates"""
        seen_ids = set()
        merged = []
        
        # Zone tips first (higher priority)
        for tip in zone_tips:
            tip_id = tip.get("id")
            if tip_id and tip_id not in seen_ids:
                seen_ids.add(tip_id)
                merged.append({**tip, "source": "zone"})
        
        # Then emotion tips
        for tip in emotion_tips:
            tip_id = tip.get("id")
            if tip_id and tip_id not in seen_ids:
                seen_ids.add(tip_id)
                merged.append({**tip, "source": "emotion"})
        
        return merged
    
    def _select_tips(
        self,
        tips: List[Dict[str, Any]],
        count: int
    ) -> List[Dict[str, Any]]:
        """Select tips with variety in categories"""
        if len(tips) <= count:
            return tips
        
        # Try to get variety in categories
        categories_seen = set()
        selected = []
        remaining = []
        
        for tip in tips:
            category = tip.get("category", "general")
            if category not in categories_seen and len(selected) < count:
                categories_seen.add(category)
                selected.append(tip)
            else:
                remaining.append(tip)
        
        # Fill remaining slots
        while len(selected) < count and remaining:
            selected.append(remaining.pop(0))
        
        return selected
    
    def format_tips_message(
        self,
        tips: List[Dict[str, Any]],
        language: str = "id"
    ) -> str:
        """
        Format tips for display to user
        
        Args:
            tips: List of tip dicts
            language: Output language
            
        Returns:
            Formatted tips message
        """
        if not tips:
            if language == "id":
                return "Teruslah menjaga kesejahteraanmu dengan cara yang sudah kamu lakukan!"
            else:
                return "Keep taking care of your wellbeing in the ways you already do!"
        
        if language == "id":
            message = "🌟 **Tips untukmu:**\n"
        else:
            message = "🌟 **Tips for you:**\n"
        
        for i, tip in enumerate(tips, 1):
            name = tip.get("name", "Tip")
            description = tip.get("description", "")
            duration = tip.get("duration", "")
            
            message += f"\n**{i}. {name}**"
            if description:
                message += f"\n   {description}"
            if duration:
                if language == "id":
                    message += f"\n   ⏱️ Durasi: {duration}"
                else:
                    message += f"\n   ⏱️ Duration: {duration}"
        
        return message
    
    def get_quick_tip(
        self,
        zone: WellnessZoneEnum,
        language: str = "id"
    ) -> str:
        """
        Get a single quick tip for a zone
        
        Args:
            zone: Wellness zone
            language: Output language
            
        Returns:
            Quick tip string
        """
        quick_tips = {
            WellnessZoneEnum.SEIMBANG: {
                "id": "Terus pertahankan kebiasaan baikmu! Coba luangkan waktu sebentar untuk hal yang kamu sukai hari ini. 🌈",
                "en": "Keep up your good habits! Try to take a moment for something you enjoy today. 🌈"
            },
            WellnessZoneEnum.BERADAPTASI: {
                "id": "Coba tarik napas dalam 3 kali dan rasakan kedua kakimu menyentuh lantai. Kamu sedang di sini, sekarang. 🌱",
                "en": "Try taking 3 deep breaths and feel both feet touching the ground. You are here, now. 🌱"
            },
            WellnessZoneEnum.BUTUH_DUKUNGAN: {
                "id": "Ingat, tidak harus menyelesaikan semuanya sendiri. Coba bicara dengan satu orang yang kamu percaya hari ini. 💙",
                "en": "Remember, you don't have to solve everything alone. Try talking to one person you trust today. 💙"
            },
            WellnessZoneEnum.PERLU_PERHATIAN: {
                "id": "Perasaanmu penting. Tolong bicara dengan guru BK atau orang dewasa yang kamu percaya. Kamu layak mendapat dukungan. 🤝",
                "en": "Your feelings matter. Please talk to a counselor or trusted adult. You deserve support. 🤝"
            }
        }
        
        zone_tips = quick_tips.get(zone, quick_tips[WellnessZoneEnum.BERADAPTASI])
        return zone_tips.get(language, zone_tips["id"])
    
    def get_closing_message(
        self,
        context: SessionContext,
        language: str = "id"
    ) -> str:
        """
        Get closing message for end of session
        
        Args:
            context: Session context
            language: Output language
            
        Returns:
            Closing message
        """
        zone = context.wellness_zone
        
        # Zone-appropriate closings
        if zone == WellnessZoneEnum.SEIMBANG:
            if language == "id":
                return """Terima kasih sudah berbagi hari ini! 🌟

Kamu sudah dalam kondisi yang baik. Terus jaga kesejahteraanmu ya!

Sampai jumpa lagi! 💙"""
            else:
                return """Thank you for sharing today! 🌟

You're in a good place. Keep taking care of your wellbeing!

See you again! 💙"""
        
        elif zone == WellnessZoneEnum.BERADAPTASI:
            if language == "id":
                return """Terima kasih sudah meluangkan waktu untuk berbicara. 🌱

Ingat, menghadapi tantangan adalah bagian normal dari kehidupan. Kamu sudah melakukan yang terbaik!

Jika kapan-kapan merasa perlu bicara lagi, aku selalu di sini. 💙"""
            else:
                return """Thank you for taking the time to talk. 🌱

Remember, facing challenges is a normal part of life. You're doing your best!

If you ever feel the need to talk again, I'm always here. 💙"""
        
        elif zone == WellnessZoneEnum.BUTUH_DUKUNGAN:
            if language == "id":
                return """Terima kasih sudah berbagi dan percaya untuk bercerita. 💙

Aku harap refleksi dan tips yang kita bahas bisa membantu sedikit. 

Ingat, kamu tidak sendirian. Jangan ragu untuk bicara dengan guru BK atau orang dewasa yang kamu percaya ya.

Aku selalu di sini jika kamu mau bicara lagi. 🤗"""
            else:
                return """Thank you for sharing and trusting me with your story. 💙

I hope the reflection and tips we discussed can help a little.

Remember, you're not alone. Don't hesitate to talk to a counselor or trusted adult.

I'm always here if you want to talk again. 🤗"""
        
        else:  # PERLU_PERHATIAN
            if language == "id":
                return """Terima kasih sudah berbagi. 💙

Yang kamu rasakan itu penting, dan aku ingin kamu mendapat dukungan yang tepat.

Tolong bicara dengan guru BK atau orang dewasa yang kamu percaya ya. Mereka bisa membantu lebih dari yang aku bisa.

Kamu berharga, dan kamu pantas mendapat bantuan. 🤝"""
            else:
                return """Thank you for sharing. 💙

What you're feeling matters, and I want you to get the right support.

Please talk to a counselor or trusted adult. They can help more than I can.

You are valuable, and you deserve help. 🤝"""


# Singleton instance
_tips_service: Optional[TipsService] = None


def get_tips_service() -> TipsService:
    """Get or create TipsService singleton"""
    global _tips_service
    if _tips_service is None:
        _tips_service = TipsService()
    return _tips_service
