"""
Question Service
Mengelola pertanyaan refleksi untuk Fase 2
"""
from typing import Dict, Any, List, Optional
import logging

from core.knowledge.question_selector import get_question_selector
from core.conversation.session_context import SessionContext

logger = logging.getLogger(__name__)


class QuestionService:
    """
    Service untuk mengelola pertanyaan refleksi
    
    Flow:
    1. Load 5 pertanyaan berdasarkan emosi yang terdeteksi
    2. Ajukan pertanyaan satu per satu
    3. Simpan jawaban user
    4. Track progress (0-5)
    """
    
    def __init__(self):
        """Initialize dengan question selector"""
        self.selector = get_question_selector()
    
    def load_questions_for_session(
        self,
        context: SessionContext
    ) -> List[Dict[str, Any]]:
        """
        Load pertanyaan untuk session berdasarkan emosi terdeteksi
        
        Args:
            context: Session context dengan emosi terdeteksi
            
        Returns:
            List of 5 questions
        """
        # Get mixed questions (3 reflection + 2 MC)
        questions = self.selector.get_mixed_questions(
            primary_emotion=context.primary_emotion or "sad",
            secondary_emotion=context.secondary_emotion,
            tertiary_emotion=context.tertiary_emotion,
            reflection_count=3,
            mc_count=2
        )
        
        # Store in context
        context.reflection_questions = questions
        context.current_question_index = 0
        
        logger.info(
            f"Loaded {len(questions)} questions for session {context.session_id}"
        )
        
        return questions
    
    def get_current_question(
        self,
        context: SessionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get current question to ask
        
        Returns:
            Current question dict or None if complete
        """
        if not context.reflection_questions:
            self.load_questions_for_session(context)
        
        return context.get_current_question()
    
    def format_question_message(
        self,
        question: Dict[str, Any],
        question_number: int,
        language: str = "id"
    ) -> str:
        """
        Format question for display to user
        
        Args:
            question: Question dict
            question_number: 1-based question number
            language: Output language
            
        Returns:
            Formatted question string
        """
        q_text = question.get("question", "")
        q_type = question.get("type", "open")
        
        if language == "id":
            header = f"📝 Pertanyaan {question_number} dari 5"
        else:
            header = f"📝 Question {question_number} of 5"
        
        message = f"{header}\n\n{q_text}"
        
        # Add options for MC questions
        if q_type == "mc":
            options = question.get("options", [])
            if options:
                message += "\n"
                for i, opt in enumerate(options, 1):
                    message += f"\n{i}. {opt}"
        
        return message
    
    def process_answer(
        self,
        context: SessionContext,
        answer: str
    ) -> Dict[str, Any]:
        """
        Process user's answer to current question
        
        Args:
            context: Session context
            answer: User's answer
            
        Returns:
            Dict with processing result
        """
        current_q = self.get_current_question(context)
        
        if not current_q:
            return {
                "success": False,
                "error": "No current question",
                "is_complete": True
            }
        
        q_type = current_q.get("type", "open")
        processed_answer = answer.strip()
        
        # For MC, try to match option number
        if q_type == "mc":
            options = current_q.get("options", [])
            processed_answer = self._process_mc_answer(answer, options)
        
        # Store answer
        context.add_reflection_answer(
            question=current_q.get("question", ""),
            answer=processed_answer
        )
        
        # Check if complete
        is_complete = context.is_reflection_complete()
        
        result = {
            "success": True,
            "question_answered": current_q.get("question"),
            "answer_recorded": processed_answer,
            "questions_completed": len(context.reflection_answers),
            "is_complete": is_complete
        }
        
        if not is_complete:
            next_q = self.get_current_question(context)
            result["next_question"] = next_q
        
        return result
    
    def _process_mc_answer(
        self,
        answer: str,
        options: List[str]
    ) -> str:
        """
        Process MC answer - match to option if number given
        
        Args:
            answer: User input (could be number or text)
            options: List of option strings
            
        Returns:
            Matched option text or original answer
        """
        answer = answer.strip()
        
        # Try to match number
        try:
            num = int(answer)
            if 1 <= num <= len(options):
                return options[num - 1]
        except ValueError:
            pass
        
        # Try to match option text
        answer_lower = answer.lower()
        for opt in options:
            if answer_lower in opt.lower() or opt.lower() in answer_lower:
                return opt
        
        # Return original if no match
        return answer
    
    def get_progress_message(
        self,
        context: SessionContext,
        language: str = "id"
    ) -> str:
        """
        Get progress message for user
        
        Returns:
            Progress message string
        """
        completed = len(context.reflection_answers)
        total = 5
        
        if language == "id":
            if completed == 0:
                return "Mari kita mulai refleksi dengan beberapa pertanyaan."
            elif completed < total:
                return f"Bagus! {completed} dari {total} pertanyaan sudah dijawab."
            else:
                return "Terima kasih sudah menjawab semua pertanyaan refleksi! 🙏"
        else:
            if completed == 0:
                return "Let's start the reflection with some questions."
            elif completed < total:
                return f"Great! {completed} of {total} questions answered."
            else:
                return "Thank you for answering all reflection questions! 🙏"
    
    def get_summary(self, context: SessionContext) -> Dict[str, Any]:
        """
        Get summary of all Q&A for narrative generation
        
        Returns:
            Summary dict
        """
        return {
            "total_questions": len(context.reflection_questions),
            "total_answers": len(context.reflection_answers),
            "is_complete": context.is_reflection_complete(),
            "qa_pairs": context.reflection_answers
        }


# Singleton instance
_question_service: Optional[QuestionService] = None


def get_question_service() -> QuestionService:
    """Get or create QuestionService singleton"""
    global _question_service
    if _question_service is None:
        _question_service = QuestionService()
    return _question_service
