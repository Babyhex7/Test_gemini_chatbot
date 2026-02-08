"""
Safe Framing
Memformat respons dengan framing yang aman dan sesuai MHCM
"""
from typing import Dict, Any, Optional, List
import logging

from modules.safety.boundary_checker import RiskLevel

logger = logging.getLogger(__name__)


class SafeFramer:
    """
    Framer untuk respons yang aman
    
    Prinsip:
    1. Validasi tanpa menghakimi
    2. Bahasa yang memberdayakan
    3. Tidak memberikan diagnosa
    4. Mendorong dukungan profesional jika perlu
    """
    
    # Pre-built safe responses for different scenarios
    RESPONSES = {
        "id": {
            "escalation": """Aku mendengar bahwa kamu sedang melewati waktu yang sangat berat, dan perasaanmu itu valid. 

Aku ingin kamu tahu bahwa kamu tidak sendirian. Aku sangat menyarankan untuk berbicara dengan orang dewasa yang kamu percaya - bisa guru BK, orang tua, atau konselor sekolah. 

Apakah ada orang dewasa di sekitarmu yang bisa kamu ajak bicara sekarang?""",
            
            "clinical_redirect": """Aku mengerti kamu ingin memahami lebih dalam tentang apa yang kamu rasakan. 

Sebagai chatbot, aku tidak bisa memberikan diagnosa atau saran medis. Tapi aku bisa menemanimu merefleksikan perasaanmu.

Jika kamu ingin penjelasan lebih profesional, aku sarankan berbicara dengan konselor sekolah atau tenaga kesehatan.

Mau lanjut cerita tentang apa yang kamu rasakan?""",
            
            "inappropriate_decline": """Maaf, aku tidak bisa membantu dengan topik itu. 

Aku di sini untuk mendengarkan dan menemani kamu merefleksikan perasaan terkait kesejahteraan emosionalmu.

Ada hal lain yang ingin kamu ceritakan tentang perasaanmu hari ini?""",
            
            "validation_base": """Terima kasih sudah berbagi. Perasaan yang kamu rasakan itu valid, dan wajar untuk merasa seperti itu.""",
            
            "empowerment_base": """Aku melihat bahwa kamu sudah berani untuk menghadapi dan memproses perasaanmu. Itu adalah kekuatan yang luar biasa.""",
            
            "closing_safe": """Ingat, tidak ada yang salah dengan mencari bantuan. Jika kamu merasa perlu bicara lebih lanjut, guru BK atau orang dewasa yang kamu percaya bisa menjadi tempat yang aman."""
        },
        "en": {
            "escalation": """I hear that you're going through a really tough time, and your feelings are valid.

I want you to know that you're not alone. I strongly suggest talking to a trusted adult - it could be a school counselor, parent, or teacher.

Is there an adult near you that you can talk to now?""",
            
            "clinical_redirect": """I understand you want to understand more about what you're feeling.

As a chatbot, I can't provide diagnoses or medical advice. But I can accompany you in reflecting on your feelings.

If you want more professional explanation, I suggest talking to a school counselor or healthcare provider.

Would you like to continue sharing about how you're feeling?""",
            
            "inappropriate_decline": """Sorry, I can't help with that topic.

I'm here to listen and accompany you in reflecting on feelings related to your emotional wellbeing.

Is there something else about your feelings today that you'd like to share?""",
            
            "validation_base": """Thank you for sharing. What you're feeling is valid, and it's okay to feel this way.""",
            
            "empowerment_base": """I see that you've been brave in facing and processing your feelings. That takes real strength.""",
            
            "closing_safe": """Remember, there's nothing wrong with seeking help. If you feel the need to talk more, a school counselor or trusted adult can be a safe space."""
        }
    }
    
    def __init__(self):
        """Initialize safe framer"""
        pass
    
    def get_response(
        self,
        response_type: str,
        language: str = "id"
    ) -> str:
        """
        Get pre-built safe response
        
        Args:
            response_type: Type of response needed
            language: Output language
            
        Returns:
            Safe response string
        """
        lang_responses = self.RESPONSES.get(language, self.RESPONSES["id"])
        return lang_responses.get(response_type, "")
    
    def frame_validation(
        self,
        emotion: str,
        language: str = "id"
    ) -> str:
        """
        Create validation statement for an emotion
        
        Args:
            emotion: Detected emotion label
            language: Output language
            
        Returns:
            Validation statement
        """
        if language == "id":
            return f"Aku mendengar bahwa kamu sedang merasa {emotion}. Perasaan itu valid, dan terima kasih sudah mau berbagi."
        else:
            return f"I hear that you're feeling {emotion}. That feeling is valid, and thank you for sharing."
    
    def frame_for_risk_level(
        self,
        risk_level: str,
        original_response: str,
        language: str = "id"
    ) -> str:
        """
        Adjust response based on risk level
        
        Args:
            risk_level: Risk level from boundary checker
            original_response: Original bot response
            language: Output language
            
        Returns:
            Framed response
        """
        if risk_level == RiskLevel.CRITICAL.value:
            return self.get_response("escalation", language)
        
        if risk_level == RiskLevel.HIGH.value:
            # Add safety reminder to response
            reminder = self.get_response("closing_safe", language)
            return f"{original_response}\n\n{reminder}"
        
        if risk_level == RiskLevel.MEDIUM.value:
            # Add subtle validation
            validation = self.get_response("validation_base", language)
            return f"{validation}\n\n{original_response}"
        
        return original_response
    
    def create_empowering_transition(
        self,
        from_phase: str,
        to_phase: str,
        language: str = "id"
    ) -> str:
        """
        Create empowering transition message between phases
        
        Args:
            from_phase: Current phase
            to_phase: Next phase
            language: Output language
            
        Returns:
            Transition message
        """
        transitions = {
            "id": {
                ("bercerita", "refleksi_ringan"): 
                    "Terima kasih sudah berbagi ceritamu. Sekarang, aku ingin mengajak kamu untuk merefleksikan perasaanmu lebih dalam melalui beberapa pertanyaan.",
                
                ("refleksi_ringan", "narasi_reflektif"):
                    "Luar biasa! Kamu sudah menjawab semua pertanyaan refleksi. Sekarang izinkan aku merangkum apa yang kita bicarakan.",
                
                ("narasi_reflektif", "tips_closing"):
                    "Berdasarkan refleksi kita, aku punya beberapa tips yang mungkin bisa membantu.",
                
                ("tips_closing", "selesai"):
                    "Terima kasih sudah meluangkan waktu untuk berbicara. Ingat, kamu tidak sendirian. 💙"
            },
            "en": {
                ("bercerita", "refleksi_ringan"):
                    "Thank you for sharing your story. Now, I'd like to invite you to reflect more deeply on your feelings through some questions.",
                
                ("refleksi_ringan", "narasi_reflektif"):
                    "Wonderful! You've answered all the reflection questions. Now let me summarize what we've discussed.",
                
                ("narasi_reflektif", "tips_closing"):
                    "Based on our reflection, I have some tips that might help.",
                
                ("tips_closing", "selesai"):
                    "Thank you for taking the time to talk. Remember, you're not alone. 💙"
            }
        }
        
        lang_transitions = transitions.get(language, transitions["id"])
        key = (from_phase.lower(), to_phase.lower())
        
        return lang_transitions.get(key, "")
    
    def sanitize_bot_response(
        self,
        response: str
    ) -> str:
        """
        Sanitize bot response to remove any clinical language
        
        Args:
            response: Raw bot response
            
        Returns:
            Sanitized response
        """
        # Words to avoid in bot responses
        avoid_words = [
            ("depresi", "kesedihan mendalam"),
            ("anxiety disorder", "kecemasan"),
            ("trauma", "pengalaman berat"),
            ("mental illness", "tantangan emosional"),
            ("diagnosa", "pemahaman"),
            ("gangguan", "tantangan"),
            ("disorder", "challenge"),
            ("disease", "difficulty"),
            ("abnormal", "unusual")
        ]
        
        result = response
        for avoid, replace in avoid_words:
            result = result.replace(avoid, replace)
            result = result.replace(avoid.capitalize(), replace.capitalize())
        
        return result
    
    def add_resource_reminder(
        self,
        message: str,
        language: str = "id"
    ) -> str:
        """
        Add gentle resource reminder to message
        
        Args:
            message: Original message
            language: Output language
            
        Returns:
            Message with resource reminder
        """
        if language == "id":
            reminder = "\n\n💡 Jika kamu merasa perlu bicara dengan seseorang, guru BK di sekolahmu siap membantu."
        else:
            reminder = "\n\n💡 If you feel the need to talk to someone, your school counselor is there to help."
        
        return message + reminder


# Singleton instance
_safe_framer: Optional[SafeFramer] = None


def get_safe_framer() -> SafeFramer:
    """Get or create SafeFramer singleton"""
    global _safe_framer
    if _safe_framer is None:
        _safe_framer = SafeFramer()
    return _safe_framer
