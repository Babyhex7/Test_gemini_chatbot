"""
Narrative Generator
Generate narasi reflektif menggunakan pendekatan MHCM
"""
from typing import Dict, Any, List, Optional
import logging

from core.llm.gemini_client import get_gemini_client
from core.conversation.session_context import SessionContext
from database.models.session import WellnessZoneEnum

logger = logging.getLogger(__name__)


class NarrativeGenerationError(Exception):
    """Error saat generation narasi gagal"""
    pass


class NarrativeGenerator:
    """
    Generator untuk narasi reflektif MHCM
    
    Menggunakan Gemini API Call #2 untuk:
    1. Merefleksikan cerita user + jawaban Q&A
    2. Menghasilkan narasi yang memvalidasi
    3. Mengidentifikasi kekuatan user
    """
    
    def __init__(self):
        """Initialize dengan gemini client"""
        self.gemini_client = get_gemini_client()
    
    async def generate(
        self,
        context: SessionContext,
        language: str = "id"
    ) -> Dict[str, Any]:
        """
        Generate narasi reflektif berdasarkan session context
        
        Args:
            context: Session context dengan story + Q&A lengkap
            language: Output language (id/en)
            
        Returns:
            Dict dengan narrative, wellness_zone, insights, strengths
        """
        if not context.is_reflection_complete():
            raise NarrativeGenerationError(
                "Cannot generate narrative: reflection not complete"
            )
        
        if not context.can_call_gemini():
            # Fallback to template-based narrative
            logger.warning("Gemini call limit reached, using template narrative")
            return self._generate_template_narrative(context, language)
        
        try:
            # Prepare data for generation
            detected_emotion = {
                "primary_emotion": context.primary_emotion,
                "secondary_emotion": context.secondary_emotion,
                "tertiary_emotion": context.tertiary_emotion,
                "wellness_zone": context.wellness_zone.value
            }
            
            # Call Gemini
            result = await self.gemini_client.generate_narrative(
                user_story=context.user_story,
                detected_emotion=detected_emotion,
                reflection_qa=context.reflection_answers,
                language=language
            )
            
            # Track Gemini call
            context.increment_gemini_call()
            
            # Store in context
            context.set_narrative(result)
            
            logger.info(
                f"Narrative generated for session {context.session_id}, "
                f"zone: {result.get('wellness_zone')}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {str(e)}")
            # Fallback to template
            return self._generate_template_narrative(context, language)
    
    def _generate_template_narrative(
        self,
        context: SessionContext,
        language: str = "id"
    ) -> Dict[str, Any]:
        """
        Generate template-based narrative as fallback
        
        Args:
            context: Session context
            language: Output language
            
        Returns:
            Template narrative dict
        """
        emotion = context.primary_emotion or "emosi"
        zone = context.wellness_zone
        
        if language == "id":
            narrative = self._get_indonesian_template(emotion, zone, context)
        else:
            narrative = self._get_english_template(emotion, zone, context)
        
        result = {
            "narrative": narrative,
            "wellness_zone": zone.value,
            "insights": self._extract_simple_insights(context, language),
            "strengths_identified": self._identify_simple_strengths(context, language)
        }
        
        context.set_narrative(result)
        return result
    
    def _get_indonesian_template(
        self,
        emotion: str,
        zone: WellnessZoneEnum,
        context: SessionContext
    ) -> str:
        """Generate Indonesian template narrative"""
        
        # Opening - validate
        opening = f"""Terima kasih sudah berbagi ceritamu. Aku mendengar bahwa kamu sedang merasakan {emotion}, dan perasaan itu sangat valid."""
        
        # Middle - reflect on answers
        middle = """

Dari refleksi yang kita lakukan bersama, aku melihat bahwa kamu sudah meluangkan waktu untuk memahami perasaanmu lebih dalam. """
        
        # Add insight based on answers if available
        if context.reflection_answers:
            first_answer = context.reflection_answers[0].get("answer", "")
            if first_answer:
                middle += f"""Kamu menyebutkan bahwa "{first_answer[:50]}..." - ini menunjukkan bahwa kamu sudah mulai memproses apa yang kamu rasakan."""
        
        # Zone-specific closing
        if zone == WellnessZoneEnum.SEIMBANG:
            closing = """

Sepertinya kamu berada di tempat yang cukup baik saat ini. Terus pertahankan kesadaran diri yang sudah kamu miliki!"""
        
        elif zone == WellnessZoneEnum.BERADAPTASI:
            closing = """

Wajar jika kadang kita menghadapi tantangan. Yang penting adalah kamu sudah menyadari perasaanmu dan mencari cara untuk mengatasinya."""
        
        elif zone == WellnessZoneEnum.BUTUH_DUKUNGAN:
            closing = """

Aku ingin kamu tahu bahwa merasa seperti ini tidak berarti ada yang salah denganmu. Kadang kita perlu sedikit bantuan ekstra, dan itu sangat normal."""
        
        else:  # PERLU_PERHATIAN
            closing = """

Perasaanmu penting, dan aku sarankan untuk berbicara dengan orang dewasa yang kamu percaya. Mereka bisa memberikan dukungan yang lebih mendalam."""
        
        return opening + middle + closing
    
    def _get_english_template(
        self,
        emotion: str,
        zone: WellnessZoneEnum,
        context: SessionContext
    ) -> str:
        """Generate English template narrative"""
        
        opening = f"""Thank you for sharing your story. I hear that you're feeling {emotion}, and that feeling is completely valid."""
        
        middle = """

From the reflection we did together, I see that you've taken time to understand your feelings more deeply. """
        
        if context.reflection_answers:
            first_answer = context.reflection_answers[0].get("answer", "")
            if first_answer:
                middle += f"""You mentioned "{first_answer[:50]}..." - this shows that you're already processing what you're feeling."""
        
        if zone == WellnessZoneEnum.SEIMBANG:
            closing = """

It seems like you're in a pretty good place right now. Keep maintaining this self-awareness you have!"""
        
        elif zone == WellnessZoneEnum.BERADAPTASI:
            closing = """

It's normal to face challenges sometimes. What matters is that you're aware of your feelings and looking for ways to cope."""
        
        elif zone == WellnessZoneEnum.BUTUH_DUKUNGAN:
            closing = """

I want you to know that feeling this way doesn't mean something is wrong with you. Sometimes we need a little extra help, and that's completely normal."""
        
        else:
            closing = """

Your feelings matter, and I suggest talking to a trusted adult. They can provide more in-depth support."""
        
        return opening + middle + closing
    
    def _extract_simple_insights(
        self,
        context: SessionContext,
        language: str = "id"
    ) -> List[str]:
        """Extract simple insights from Q&A"""
        insights = []
        
        if not context.reflection_answers:
            return insights
        
        # Simple insight based on number of answers
        count = len(context.reflection_answers)
        
        if language == "id":
            insights.append(f"Kamu sudah merefleksikan {count} aspek dari perasaanmu")
            insights.append("Kamu menunjukkan kesadaran diri yang baik")
        else:
            insights.append(f"You reflected on {count} aspects of your feelings")
            insights.append("You show good self-awareness")
        
        return insights
    
    def _identify_simple_strengths(
        self,
        context: SessionContext,
        language: str = "id"
    ) -> List[str]:
        """Identify simple strengths"""
        strengths = []
        
        if language == "id":
            strengths.append("Kesediaan untuk berbagi dan terbuka")
            strengths.append("Kemampuan untuk merefleksikan perasaan")
        else:
            strengths.append("Willingness to share and be open")
            strengths.append("Ability to reflect on feelings")
        
        return strengths
    
    def format_narrative_message(
        self,
        narrative_data: Dict[str, Any],
        language: str = "id"
    ) -> str:
        """
        Format narrative for display to user
        
        Args:
            narrative_data: Result from generate()
            language: Output language
            
        Returns:
            Formatted narrative message
        """
        narrative = narrative_data.get("narrative", "")
        insights = narrative_data.get("insights", [])
        strengths = narrative_data.get("strengths_identified", [])
        
        if language == "id":
            message = f"💭 **Refleksi**\n\n{narrative}"
            
            if strengths:
                message += "\n\n✨ **Kekuatanmu:**"
                for s in strengths[:2]:
                    message += f"\n• {s}"
        else:
            message = f"💭 **Reflection**\n\n{narrative}"
            
            if strengths:
                message += "\n\n✨ **Your Strengths:**"
                for s in strengths[:2]:
                    message += f"\n• {s}"
        
        return message


# Singleton instance
_narrative_generator: Optional[NarrativeGenerator] = None


def get_narrative_generator() -> NarrativeGenerator:
    """Get or create NarrativeGenerator singleton"""
    global _narrative_generator
    if _narrative_generator is None:
        _narrative_generator = NarrativeGenerator()
    return _narrative_generator
