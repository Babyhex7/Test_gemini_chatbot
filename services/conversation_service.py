"""
Conversation Service
Orchestrator utama untuk alur percakapan 4-fase
"""
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.session import ChatSession, PhaseEnum, WellnessZoneEnum
from database.models.message import Message, MessageRole
from database.models.emotion_log import EmotionLog
from database.models.reflection import Reflection

from core.conversation.session_context import SessionContext
from core.conversation.phase_manager import get_phase_manager, PhaseTransitionError
from core.knowledge.loader import get_knowledge_loader

from modules.emotion.detector import get_emotion_detector
from modules.emotion.zone_mapper import get_zone_mapper
from modules.reflection.question_service import get_question_service
from modules.reflection.narrative_generator import get_narrative_generator
from modules.safety.boundary_checker import get_boundary_checker, RiskLevel
from modules.safety.safe_framing import get_safe_framer
from modules.tips.tips_service import get_tips_service

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Main orchestrator untuk conversation flow
    
    Flow: BERCERITA → REFLEKSI_RINGAN → NARASI_REFLEKTIF → TIPS_CLOSING → SELESAI
    """
    
    def __init__(self):
        """Initialize dengan semua dependencies"""
        self.phase_manager = get_phase_manager()
        self.knowledge_loader = get_knowledge_loader()
        self.emotion_detector = get_emotion_detector()
        self.zone_mapper = get_zone_mapper()
        self.question_service = get_question_service()
        self.narrative_generator = get_narrative_generator()
        self.boundary_checker = get_boundary_checker()
        self.safe_framer = get_safe_framer()
        self.tips_service = get_tips_service()
        
        # In-memory session contexts
        self._contexts: Dict[int, SessionContext] = {}
    
    async def start_session(
        self,
        db: AsyncSession,
        user_id: int,
        language: str = "id"
    ) -> Tuple[ChatSession, str]:
        """
        Start new chat session
        
        Args:
            db: Database session
            user_id: User ID
            language: Preferred language
            
        Returns:
            Tuple of (ChatSession, greeting message)
        """
        # Create session in DB
        session = ChatSession(
            user_id=user_id,
            current_phase=PhaseEnum.BERCERITA,
            language=language
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Create in-memory context
        context = SessionContext(
            session_id=session.id,
            user_id=user_id
        )
        self._contexts[session.id] = context
        
        # Generate greeting
        greeting = self._get_greeting(language)
        
        # Save greeting as bot message
        await self._save_message(
            db=db,
            session_id=session.id,
            role=MessageRole.BOT,
            content=greeting,
            phase=PhaseEnum.BERCERITA
        )
        
        logger.info(f"Started session {session.id} for user {user_id}")
        
        return session, greeting
    
    async def process_message(
        self,
        db: AsyncSession,
        session_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            db: Database session
            session_id: Chat session ID
            user_message: User's message
            
        Returns:
            Dict with response and metadata
        """
        # Get or create context
        context = await self._get_context(db, session_id)
        if not context:
            return {
                "error": "Session not found",
                "response": "Maaf, sesi tidak ditemukan. Silakan mulai sesi baru."
            }
        
        # Update activity
        context.update_activity()
        
        # Save user message
        await self._save_message(
            db=db,
            session_id=session_id,
            role=MessageRole.USER,
            content=user_message,
            phase=context.current_phase
        )
        
        # Check safety boundaries
        safety_check = self.boundary_checker.check_message(user_message)
        
        if safety_check["action"] == "ESCALATE_IMMEDIATELY":
            response = await self._handle_escalation(db, context)
            return response
        
        if safety_check["action"] == "REDIRECT_POLITELY":
            response = self.safe_framer.get_response(
                "clinical_redirect",
                db.get_session() if hasattr(db, 'get_session') else "id"
            )
            await self._save_message(
                db=db,
                session_id=session_id,
                role=MessageRole.BOT,
                content=response,
                phase=context.current_phase
            )
            return {"response": response, "phase": context.current_phase.value}
        
        if safety_check["action"] == "DECLINE_POLITELY":
            response = self.safe_framer.get_response("inappropriate_decline", "id")
            await self._save_message(
                db=db,
                session_id=session_id,
                role=MessageRole.BOT,
                content=response,
                phase=context.current_phase
            )
            return {"response": response, "phase": context.current_phase.value}
        
        # Process based on current phase
        response = await self._process_by_phase(db, context, user_message, safety_check)
        
        return response
    
    async def _process_by_phase(
        self,
        db: AsyncSession,
        context: SessionContext,
        user_message: str,
        safety_check: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message based on current phase"""
        
        phase = context.current_phase
        
        if phase == PhaseEnum.BERCERITA:
            return await self._handle_bercerita(db, context, user_message, safety_check)
        
        elif phase == PhaseEnum.REFLEKSI_RINGAN:
            return await self._handle_refleksi(db, context, user_message)
        
        elif phase == PhaseEnum.NARASI_REFLEKTIF:
            return await self._handle_narasi(db, context, user_message)
        
        elif phase == PhaseEnum.TIPS_CLOSING:
            return await self._handle_tips(db, context, user_message)
        
        elif phase == PhaseEnum.SELESAI:
            return await self._handle_selesai(db, context, user_message)
        
        return {"error": "Unknown phase", "response": "Terjadi kesalahan sistem."}
    
    async def _handle_bercerita(
        self,
        db: AsyncSession,
        context: SessionContext,
        user_message: str,
        safety_check: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle BERCERITA phase - story + emotion detection"""
        
        # Accumulate user story
        if context.user_story:
            context.user_story += f"\n{user_message}"
        else:
            context.user_story = user_message
        
        # Check if story is sufficient (simple length check)
        if len(context.user_story) < 50:
            response = self._get_clarifying_question("id")
            await self._save_message(
                db=db,
                session_id=context.session_id,
                role=MessageRole.BOT,
                content=response,
                phase=PhaseEnum.BERCERITA
            )
            return {"response": response, "phase": "bercerita"}
        
        # Detect emotion (Gemini Call #1)
        try:
            emotion_result = await self.emotion_detector.detect(context.user_story)
            context.set_detected_emotion(emotion_result)
            context.increment_gemini_call()
            
            # Apply zone safety check
            final_zone = self.zone_mapper.determine_zone(
                detected_zone=emotion_result.get("wellness_zone", "beradaptasi"),
                user_text=context.user_story,
                emotion_confidence=emotion_result.get("confidence", "medium")
            )
            context.wellness_zone = final_zone
            
            # Log emotion
            await self._log_emotion(db, context, emotion_result)
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            # Fallback
            context.primary_emotion = "sad"
            context.wellness_zone = WellnessZoneEnum.BERADAPTASI
        
        # Load reflection questions
        self.question_service.load_questions_for_session(context)
        
        # Transition to REFLEKSI_RINGAN
        context.current_phase = PhaseEnum.REFLEKSI_RINGAN
        
        # Update session in DB
        await self._update_session(db, context)
        
        # Generate transition + first question
        transition = self.safe_framer.create_empowering_transition(
            "bercerita", "refleksi_ringan", "id"
        )
        
        first_q = context.get_current_question()
        q_message = self.question_service.format_question_message(first_q, 1, "id")
        
        response = f"{transition}\n\n{q_message}"
        
        await self._save_message(
            db=db,
            session_id=context.session_id,
            role=MessageRole.BOT,
            content=response,
            phase=PhaseEnum.REFLEKSI_RINGAN
        )
        
        return {
            "response": response,
            "phase": "refleksi_ringan",
            "emotion_detected": {
                "primary": context.primary_emotion,
                "secondary": context.secondary_emotion,
                "wellness_zone": context.wellness_zone.value
            }
        }
    
    async def _handle_refleksi(
        self,
        db: AsyncSession,
        context: SessionContext,
        user_message: str
    ) -> Dict[str, Any]:
        """Handle REFLEKSI_RINGAN phase - Q&A"""
        
        # Process answer
        result = self.question_service.process_answer(context, user_message)
        
        if result["is_complete"]:
            # Transition to NARASI_REFLEKTIF
            context.current_phase = PhaseEnum.NARASI_REFLEKTIF
            await self._update_session(db, context)
            
            # Generate narrative (Gemini Call #2)
            try:
                narrative_result = await self.narrative_generator.generate(context, "id")
                
                transition = self.safe_framer.create_empowering_transition(
                    "refleksi_ringan", "narasi_reflektif", "id"
                )
                
                narrative_message = self.narrative_generator.format_narrative_message(
                    narrative_result, "id"
                )
                
                response = f"{transition}\n\n{narrative_message}"
                
            except Exception as e:
                logger.error(f"Narrative generation failed: {e}")
                response = "Terima kasih sudah menjawab semua pertanyaan. " + \
                           context.mhcm_narrative if context.mhcm_narrative else \
                           "Aku melihat kamu sudah meluangkan waktu untuk merefleksikan perasaanmu."
            
            await self._save_message(
                db=db,
                session_id=context.session_id,
                role=MessageRole.BOT,
                content=response,
                phase=PhaseEnum.NARASI_REFLEKTIF
            )
            
            # Save reflection to DB
            await self._save_reflection(db, context)
            
            # Auto-transition to TIPS_CLOSING
            return await self._transition_to_tips(db, context)
        
        else:
            # Get next question
            next_q = result.get("next_question")
            q_num = result["questions_completed"] + 1
            
            if next_q:
                response = self.question_service.format_question_message(next_q, q_num, "id")
            else:
                response = self.question_service.get_progress_message(context, "id")
            
            await self._save_message(
                db=db,
                session_id=context.session_id,
                role=MessageRole.BOT,
                content=response,
                phase=PhaseEnum.REFLEKSI_RINGAN
            )
            
            return {
                "response": response,
                "phase": "refleksi_ringan",
                "questions_completed": result["questions_completed"]
            }
    
    async def _handle_narasi(
        self,
        db: AsyncSession,
        context: SessionContext,
        user_message: str
    ) -> Dict[str, Any]:
        """Handle NARASI_REFLEKTIF phase"""
        # This phase is mostly bot-driven, just acknowledge user
        return await self._transition_to_tips(db, context)
    
    async def _transition_to_tips(
        self,
        db: AsyncSession,
        context: SessionContext
    ) -> Dict[str, Any]:
        """Transition to TIPS_CLOSING phase"""
        
        context.current_phase = PhaseEnum.TIPS_CLOSING
        await self._update_session(db, context)
        
        # Get tips
        tips = self.tips_service.get_tips_for_session(context, 3)
        
        transition = self.safe_framer.create_empowering_transition(
            "narasi_reflektif", "tips_closing", "id"
        )
        
        tips_message = self.tips_service.format_tips_message(tips, "id")
        closing = self.tips_service.get_closing_message(context, "id")
        
        response = f"{transition}\n\n{tips_message}\n\n{closing}"
        
        await self._save_message(
            db=db,
            session_id=context.session_id,
            role=MessageRole.BOT,
            content=response,
            phase=PhaseEnum.TIPS_CLOSING
        )
        
        # Transition to SELESAI
        context.current_phase = PhaseEnum.SELESAI
        await self._update_session(db, context)
        
        return {
            "response": response,
            "phase": "selesai",
            "session_complete": True
        }
    
    async def _handle_tips(
        self,
        db: AsyncSession,
        context: SessionContext,
        user_message: str
    ) -> Dict[str, Any]:
        """Handle TIPS_CLOSING phase"""
        # Session already closing, just acknowledge
        response = "Terima kasih! Jika kamu mau bicara lagi, kamu bisa memulai sesi baru kapan saja. 💙"
        
        await self._save_message(
            db=db,
            session_id=context.session_id,
            role=MessageRole.BOT,
            content=response,
            phase=PhaseEnum.SELESAI
        )
        
        context.current_phase = PhaseEnum.SELESAI
        await self._update_session(db, context)
        
        return {
            "response": response,
            "phase": "selesai",
            "session_complete": True
        }
    
    async def _handle_selesai(
        self,
        db: AsyncSession,
        context: SessionContext,
        user_message: str
    ) -> Dict[str, Any]:
        """Handle SELESAI phase - session already complete"""
        response = "Sesi ini sudah selesai. Jika kamu mau bicara lagi, silakan mulai sesi baru. 💙"
        
        return {
            "response": response,
            "phase": "selesai",
            "session_complete": True,
            "suggest_new_session": True
        }
    
    async def _handle_escalation(
        self,
        db: AsyncSession,
        context: SessionContext
    ) -> Dict[str, Any]:
        """Handle escalation situation"""
        response = self.zone_mapper.get_escalation_message("id")
        
        context.wellness_zone = WellnessZoneEnum.PERLU_PERHATIAN
        await self._update_session(db, context)
        
        await self._save_message(
            db=db,
            session_id=context.session_id,
            role=MessageRole.BOT,
            content=response,
            phase=context.current_phase,
            message_type="escalation"
        )
        
        return {
            "response": response,
            "phase": context.current_phase.value,
            "escalation": True,
            "wellness_zone": "perlu_perhatian"
        }
    
    # ===== HELPER METHODS =====
    
    async def _get_context(
        self,
        db: AsyncSession,
        session_id: int
    ) -> Optional[SessionContext]:
        """Get or load session context"""
        if session_id in self._contexts:
            return self._contexts[session_id]
        
        # Try to load from DB
        session = await db.get(ChatSession, session_id)
        if not session:
            return None
        
        # Reconstruct context
        context = SessionContext(
            session_id=session.id,
            user_id=session.user_id
        )
        context.current_phase = session.current_phase
        context.user_story = session.detected_emotion.get("user_story", "") if session.detected_emotion else ""
        
        if session.detected_emotion:
            context.set_detected_emotion(session.detected_emotion)
        
        if session.reflection_progress:
            context.reflection_answers = session.reflection_progress.get("answers", [])
            context.current_question_index = len(context.reflection_answers)
        
        context.gemini_call_count = session.gemini_call_count
        
        self._contexts[session_id] = context
        return context
    
    async def _save_message(
        self,
        db: AsyncSession,
        session_id: int,
        role: MessageRole,
        content: str,
        phase: PhaseEnum,
        message_type: str = "text"
    ) -> Message:
        """Save message to database"""
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            phase=phase,
            message_type=message_type
        )
        db.add(message)
        await db.commit()
        return message
    
    async def _update_session(
        self,
        db: AsyncSession,
        context: SessionContext
    ) -> None:
        """Update session in database"""
        session = await db.get(ChatSession, context.session_id)
        if session:
            session.current_phase = context.current_phase
            session.wellness_zone = context.wellness_zone
            session.gemini_call_count = context.gemini_call_count
            session.detected_emotion = context.detected_emotion
            session.reflection_progress = {
                "answers": context.reflection_answers,
                "questions": [q.get("question") for q in context.reflection_questions]
            }
            session.updated_at = datetime.utcnow()
            await db.commit()
    
    async def _log_emotion(
        self,
        db: AsyncSession,
        context: SessionContext,
        emotion_result: Dict[str, Any]
    ) -> None:
        """Log detected emotion to database"""
        log = EmotionLog(
            session_id=context.session_id,
            primary_emotion=emotion_result.get("primary_emotion"),
            secondary_emotion=emotion_result.get("secondary_emotion"),
            tertiary_emotion=emotion_result.get("tertiary_emotion"),
            keywords=emotion_result.get("keywords", []),
            confidence_score=0.8 if emotion_result.get("confidence") == "high" else 0.5,
            wellness_zone=context.wellness_zone
        )
        db.add(log)
        await db.commit()
    
    async def _save_reflection(
        self,
        db: AsyncSession,
        context: SessionContext
    ) -> None:
        """Save reflection to database"""
        reflection = Reflection(session_id=context.session_id)
        
        # Add all Q&A
        for qa in context.reflection_answers:
            reflection.add_answer(qa.get("question", ""), qa.get("answer", ""))
        
        reflection.mhcm_narrative = context.mhcm_narrative
        reflection.tips_ids = [t.get("id") for t in context.selected_tips]
        
        db.add(reflection)
        await db.commit()
    
    def _get_greeting(self, language: str = "id") -> str:
        """Get greeting message"""
        if language == "id":
            return """Halo! 👋 

Aku EduMindAI, teman virtual yang siap mendengarkan ceritamu.

Apa yang sedang kamu rasakan hari ini? Ceritakan saja, aku di sini untuk mendengarkan. 💙"""
        else:
            return """Hello! 👋

I'm EduMindAI, a virtual friend ready to listen to your story.

What are you feeling today? Just share, I'm here to listen. 💙"""
    
    def _get_clarifying_question(self, language: str = "id") -> str:
        """Get clarifying question for short messages"""
        if language == "id":
            return "Hmm, aku ingin memahami lebih dalam. Bisa ceritakan lebih lanjut tentang apa yang kamu rasakan?"
        else:
            return "Hmm, I'd like to understand more. Can you tell me more about what you're feeling?"


# Singleton instance
_conversation_service: Optional[ConversationService] = None


def get_conversation_service() -> ConversationService:
    """Get or create ConversationService singleton"""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService()
    return _conversation_service
