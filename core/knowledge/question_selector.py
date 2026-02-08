"""
Question Selector
Memilih pertanyaan refleksi berdasarkan emosi yang terdeteksi
"""
import random
from typing import Dict, Any, List, Optional
import logging

from core.knowledge.loader import get_knowledge_loader

logger = logging.getLogger(__name__)


class QuestionSelector:
    """
    Selector untuk pertanyaan refleksi
    
    Menggunakan strategi:
    1. Cari pertanyaan di level emosi tertiary (paling spesifik)
    2. Fallback ke secondary jika tidak ada
    3. Fallback ke primary jika secondary tidak ada
    4. Gunakan default questions jika tidak ada sama sekali
    """
    
    def __init__(self):
        """Initialize dengan knowledge loader"""
        self.loader = get_knowledge_loader()
    
    def get_reflection_questions(
        self,
        primary_emotion: str,
        secondary_emotion: Optional[str] = None,
        tertiary_emotion: Optional[str] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get reflection questions untuk emosi tertentu
        
        Args:
            primary_emotion: ID emosi primary
            secondary_emotion: ID emosi secondary (optional)
            tertiary_emotion: ID emosi tertiary (optional)
            count: Jumlah pertanyaan yang diinginkan
            
        Returns:
            List of question dicts dengan format:
            {
                "id": "q1",
                "question": "...",
                "type": "open/mc",
                "options": [...] (only for mc)
            }
        """
        questions_data = self.loader.get_questions_for_emotion(
            primary_id=primary_emotion,
            secondary_id=secondary_emotion,
            tertiary_id=tertiary_emotion
        )
        
        reflection_questions = questions_data.get("reflection_questions", [])
        
        if not reflection_questions:
            logger.warning(
                f"No questions found for emotion: {primary_emotion}/{secondary_emotion}/{tertiary_emotion}"
            )
            return self._get_default_questions(count)
        
        # Ambil sesuai count yang diminta
        if len(reflection_questions) <= count:
            return reflection_questions
        
        return reflection_questions[:count]
    
    def get_mc_questions(
        self,
        primary_emotion: str,
        secondary_emotion: Optional[str] = None,
        tertiary_emotion: Optional[str] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get multiple choice questions untuk emosi tertentu
        
        Args:
            primary_emotion: ID emosi primary
            secondary_emotion: ID emosi secondary (optional)
            tertiary_emotion: ID emosi tertiary (optional)
            count: Jumlah pertanyaan MC yang diinginkan
            
        Returns:
            List of MC question dicts
        """
        questions_data = self.loader.get_questions_for_emotion(
            primary_id=primary_emotion,
            secondary_id=secondary_emotion,
            tertiary_id=tertiary_emotion
        )
        
        mc_questions = questions_data.get("mc_questions", [])
        
        if not mc_questions:
            logger.warning(
                f"No MC questions found for emotion: {primary_emotion}/{secondary_emotion}/{tertiary_emotion}"
            )
            return self._get_default_mc_questions(count)
        
        # Ambil sesuai count yang diminta
        if len(mc_questions) <= count:
            return mc_questions
        
        return mc_questions[:count]
    
    def get_mixed_questions(
        self,
        primary_emotion: str,
        secondary_emotion: Optional[str] = None,
        tertiary_emotion: Optional[str] = None,
        reflection_count: int = 3,
        mc_count: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get campuran reflection dan MC questions
        
        Format: 3 refleksi terbuka + 2 MC = 5 total
        
        Returns:
            List of mixed questions (reflection first, then MC)
        """
        reflection = self.get_reflection_questions(
            primary_emotion, secondary_emotion, tertiary_emotion, reflection_count
        )
        mc = self.get_mc_questions(
            primary_emotion, secondary_emotion, tertiary_emotion, mc_count
        )
        
        # Combine dengan tag type
        result = []
        for q in reflection:
            result.append({**q, "type": "open"})
        for q in mc:
            result.append({**q, "type": "mc"})
        
        return result
    
    def get_next_question(
        self,
        questions: List[Dict[str, Any]],
        current_index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get next question dari list
        
        Args:
            questions: List of questions
            current_index: Current question index (0-based)
            
        Returns:
            Next question or None if complete
        """
        if current_index >= len(questions):
            return None
        return questions[current_index]
    
    def _get_default_questions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Default questions jika tidak ada yang spesifik"""
        defaults = [
            {
                "id": "default_1",
                "question": "Ceritakan lebih lanjut tentang apa yang kamu rasakan saat ini?"
            },
            {
                "id": "default_2",
                "question": "Apa yang membuatmu merasakan hal tersebut?"
            },
            {
                "id": "default_3",
                "question": "Apa yang biasanya membantu kamu ketika merasakan hal seperti ini?"
            },
            {
                "id": "default_4",
                "question": "Siapa orang yang bisa kamu ajak bicara tentang ini?"
            },
            {
                "id": "default_5",
                "question": "Apa satu hal kecil yang bisa kamu lakukan untuk merasa sedikit lebih baik?"
            }
        ]
        return defaults[:count]
    
    def _get_default_mc_questions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Default MC questions jika tidak ada yang spesifik"""
        defaults = [
            {
                "id": "default_mc_1",
                "question": "Seberapa sering kamu merasakan hal seperti ini?",
                "options": ["Baru pertama kali", "Kadang-kadang", "Sering", "Hampir setiap hari"],
                "answer_key": None
            },
            {
                "id": "default_mc_2",
                "question": "Kapan biasanya kamu merasakan hal seperti ini?",
                "options": ["Pagi hari", "Siang hari", "Sore/malam", "Tidak tentu"],
                "answer_key": None
            },
            {
                "id": "default_mc_3",
                "question": "Apakah perasaan ini mempengaruhi aktivitasmu?",
                "options": ["Tidak sama sekali", "Sedikit", "Cukup banyak", "Sangat mempengaruhi"],
                "answer_key": None
            },
            {
                "id": "default_mc_4",
                "question": "Sudah berapa lama kamu merasakan hal ini?",
                "options": ["Hari ini saja", "Beberapa hari", "Minggu ini", "Lebih dari seminggu"],
                "answer_key": None
            },
            {
                "id": "default_mc_5",
                "question": "Apakah ada orang yang tahu kamu sedang merasakan hal ini?",
                "options": ["Ya, sudah cerita", "Ada tapi belum cerita", "Tidak ada", "Tidak yakin"],
                "answer_key": None
            }
        ]
        return defaults[:count]


# Singleton instance
_question_selector: Optional[QuestionSelector] = None


def get_question_selector() -> QuestionSelector:
    """Get or create QuestionSelector singleton"""
    global _question_selector
    if _question_selector is None:
        _question_selector = QuestionSelector()
    return _question_selector
