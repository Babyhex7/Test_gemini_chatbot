"""
Phase Manager
Mengelola transisi fase dalam percakapan 4-fase
"""
from typing import Dict, Any, Optional, Tuple
import logging

from database.models.session import PhaseEnum
from core.conversation.session_context import SessionContext

logger = logging.getLogger(__name__)


class PhaseTransitionError(Exception):
    """Error saat transisi fase tidak valid"""
    pass


class PhaseManager:
    """
    Manager untuk fase percakapan
    
    Flow: BERCERITA → REFLEKSI_RINGAN → NARASI_REFLEKTIF → TIPS_CLOSING → SELESAI
    
    Setiap fase memiliki:
    - Entry condition: Kondisi untuk masuk ke fase
    - Exit condition: Kondisi untuk keluar dari fase
    - Actions: Apa yang terjadi di fase tersebut
    """
    
    # Valid transitions map
    TRANSITIONS = {
        PhaseEnum.BERCERITA: PhaseEnum.REFLEKSI_RINGAN,
        PhaseEnum.REFLEKSI_RINGAN: PhaseEnum.NARASI_REFLEKTIF,
        PhaseEnum.NARASI_REFLEKTIF: PhaseEnum.TIPS_CLOSING,
        PhaseEnum.TIPS_CLOSING: PhaseEnum.SELESAI,
        PhaseEnum.SELESAI: None  # Terminal state
    }
    
    # Phase descriptions
    PHASE_INFO = {
        PhaseEnum.BERCERITA: {
            "name": "Bercerita",
            "description": "User menceritakan perasaan/masalah mereka",
            "bot_role": "Mendengarkan dengan empati, mengajukan pertanyaan klarifikasi",
            "gemini_call": True,  # Call #1: Emotion detection
            "expected_messages": "1-3"
        },
        PhaseEnum.REFLEKSI_RINGAN: {
            "name": "Refleksi Ringan",
            "description": "Bot mengajukan 5 pertanyaan refleksi",
            "bot_role": "Mengajukan pertanyaan reflection & MC",
            "gemini_call": False,
            "expected_messages": "5 Q&A pairs"
        },
        PhaseEnum.NARASI_REFLEKTIF: {
            "name": "Narasi Reflektif",
            "description": "Bot memberikan narasi MHCM berdasarkan refleksi",
            "bot_role": "Menyampaikan insight dan validasi",
            "gemini_call": True,  # Call #2: Narrative generation
            "expected_messages": "1"
        },
        PhaseEnum.TIPS_CLOSING: {
            "name": "Tips & Closing",
            "description": "Bot memberikan tips dan menutup sesi",
            "bot_role": "Memberikan tips praktis dan penutup hangat",
            "gemini_call": False,
            "expected_messages": "1-2"
        },
        PhaseEnum.SELESAI: {
            "name": "Selesai",
            "description": "Sesi telah selesai",
            "bot_role": "N/A",
            "gemini_call": False,
            "expected_messages": "0"
        }
    }
    
    def __init__(self):
        """Initialize Phase Manager"""
        pass
    
    def get_current_phase(self, context: SessionContext) -> PhaseEnum:
        """Get current phase from context"""
        return context.current_phase
    
    def get_phase_info(self, phase: PhaseEnum) -> Dict[str, Any]:
        """Get info about a specific phase"""
        return self.PHASE_INFO.get(phase, {})
    
    def can_transition(self, context: SessionContext) -> Tuple[bool, str]:
        """
        Check if we can transition to next phase
        
        Returns:
            Tuple of (can_transition: bool, reason: str)
        """
        current_phase = context.current_phase
        
        if current_phase == PhaseEnum.SELESAI:
            return False, "Sesi sudah selesai"
        
        # Check conditions per phase
        if current_phase == PhaseEnum.BERCERITA:
            # Need: user story + emotion detection
            if not context.user_story:
                return False, "User belum menceritakan masalahnya"
            if not context.primary_emotion:
                return False, "Emosi belum terdeteksi"
            return True, "Ready untuk refleksi"
        
        elif current_phase == PhaseEnum.REFLEKSI_RINGAN:
            # Need: 5 Q&A complete
            if not context.is_reflection_complete():
                answered = len(context.reflection_answers)
                return False, f"Refleksi belum selesai ({answered}/5)"
            return True, "Refleksi selesai, siap untuk narasi"
        
        elif current_phase == PhaseEnum.NARASI_REFLEKTIF:
            # Need: narrative generated
            if not context.mhcm_narrative:
                return False, "Narasi belum di-generate"
            return True, "Narasi selesai, siap untuk tips"
        
        elif current_phase == PhaseEnum.TIPS_CLOSING:
            # Can always close
            return True, "Siap untuk menutup sesi"
        
        return False, "Unknown phase"
    
    def transition(self, context: SessionContext) -> PhaseEnum:
        """
        Transition to next phase
        
        Returns:
            New phase
            
        Raises:
            PhaseTransitionError if transition not allowed
        """
        can_transition, reason = self.can_transition(context)
        
        if not can_transition:
            raise PhaseTransitionError(f"Cannot transition: {reason}")
        
        current_phase = context.current_phase
        next_phase = self.TRANSITIONS.get(current_phase)
        
        if next_phase is None:
            raise PhaseTransitionError("No valid next phase")
        
        logger.info(f"Phase transition: {current_phase.value} → {next_phase.value}")
        context.current_phase = next_phase
        
        return next_phase
    
    def should_call_gemini(self, context: SessionContext) -> bool:
        """
        Check if current phase should call Gemini API
        
        Returns:
            True if Gemini should be called
        """
        phase_info = self.PHASE_INFO.get(context.current_phase, {})
        return phase_info.get("gemini_call", False) and context.can_call_gemini()
    
    def get_bot_instructions(self, context: SessionContext) -> str:
        """
        Get bot instructions for current phase
        
        Returns:
            Instruction string for bot behavior
        """
        phase = context.current_phase
        
        if phase == PhaseEnum.BERCERITA:
            if not context.user_story:
                return """Sapa user dengan hangat dan minta mereka menceritakan apa yang sedang dirasakan.
Contoh: "Halo! Aku di sini untuk mendengarkan. Ceritakan apa yang sedang kamu rasakan hari ini?"
"""
            else:
                return """User sudah bercerita. 
Validasi perasaan mereka dan ajukan 1-2 pertanyaan klarifikasi jika perlu.
Jika sudah cukup jelas, siap untuk deteksi emosi dan transisi ke refleksi.
"""
        
        elif phase == PhaseEnum.REFLEKSI_RINGAN:
            q_num = context.current_question_index + 1
            current_q = context.get_current_question()
            if current_q:
                q_type = current_q.get("type", "open")
                return f"""Ajukan pertanyaan refleksi ke-{q_num} dari 5.
Jenis: {"Terbuka" if q_type == "open" else "Pilihan Ganda"}
Pertanyaan: {current_q.get("question", "")}
"""
            else:
                return "Semua pertanyaan sudah dijawab. Siap untuk narasi."
        
        elif phase == PhaseEnum.NARASI_REFLEKTIF:
            return """Berikan narasi reflektif berdasarkan:
1. Cerita awal user
2. Emosi yang terdeteksi
3. Jawaban dari 5 pertanyaan refleksi

Narasi harus:
- Memvalidasi pengalaman user
- Merefleksikan insight dari jawaban
- Menggunakan framing MHCM (spektrum, bukan label)
- Bersifat memberdayakan, bukan menghakimi
"""
        
        elif phase == PhaseEnum.TIPS_CLOSING:
            zone = context.wellness_zone.value
            return f"""Berikan 2-3 tips praktis berdasarkan:
- Wellness zone: {zone}
- Emosi: {context.primary_emotion}

Format:
1. Tip 1 (singkat, actionable)
2. Tip 2 (singkat, actionable)
3. Tip 3 (optional)

Tutup dengan pesan hangat dan reminder untuk bicara dengan orang dewasa terpercaya jika diperlukan.
"""
        
        elif phase == PhaseEnum.SELESAI:
            return "Sesi sudah selesai. Jika user ingin bicara lagi, sarakan untuk memulai sesi baru."
        
        return ""
    
    def get_next_action(self, context: SessionContext) -> Dict[str, Any]:
        """
        Get next action based on current phase and state
        
        Returns:
            Dict with action details
        """
        phase = context.current_phase
        can_transition, reason = self.can_transition(context)
        
        action = {
            "phase": phase.value,
            "can_transition": can_transition,
            "transition_reason": reason,
            "needs_gemini": self.should_call_gemini(context),
            "instructions": self.get_bot_instructions(context)
        }
        
        # Add phase-specific data
        if phase == PhaseEnum.REFLEKSI_RINGAN:
            action["current_question"] = context.get_current_question()
            action["questions_answered"] = len(context.reflection_answers)
            action["questions_total"] = 5
        
        elif phase == PhaseEnum.TIPS_CLOSING:
            action["wellness_zone"] = context.wellness_zone.value
            action["tips_count"] = len(context.selected_tips)
        
        return action


# Singleton instance
_phase_manager: Optional[PhaseManager] = None


def get_phase_manager() -> PhaseManager:
    """Get or create PhaseManager singleton"""
    global _phase_manager
    if _phase_manager is None:
        _phase_manager = PhaseManager()
    return _phase_manager
