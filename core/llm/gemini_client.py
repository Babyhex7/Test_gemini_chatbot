"""
Google Gemini API Client
Wrapper untuk interaksi dengan Gemini API - hanya 2 calls per session
"""
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClientError(Exception):
    """Custom exception untuk Gemini Client errors"""
    pass


class GeminiRateLimitError(GeminiClientError):
    """Exception ketika rate limit exceeded"""
    pass


class GeminiClient:
    """
    Wrapper untuk Google Gemini API
    
    Digunakan untuk:
    - Call #1: Deteksi emosi (Fase 1 - BERCERITA)
    - Call #2: Generate narasi reflektif MHCM (Fase 3 - NARASI_REFLEKTIF)
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content menggunakan Gemini API
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            
        Returns:
            Generated text response
        """
        try:
            # Combine system instruction dengan prompt jika ada
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini API")
                return ""
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise GeminiClientError(f"Failed to generate content: {str(e)}")
    
    async def detect_emotion(
        self,
        user_story: str,
        emotion_wheel_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call #1: Deteksi emosi dari cerita user menggunakan Feeling Wheel
        
        Args:
            user_story: Cerita/curhat dari user
            emotion_wheel_data: Data Feeling Wheel (JSON)
            
        Returns:
            Dict dengan primary, secondary, tertiary emotion, keywords, confidence
        """
        from core.llm.prompts import PromptManager
        
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_emotion_detection_prompt(
            user_story=user_story,
            emotion_wheel=emotion_wheel_data
        )
        
        response = await self.generate_content(prompt)
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            result = self._extract_json(response)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse emotion detection response: {response}")
            # Return default if parsing fails
            return {
                "primary_emotion": "sad",
                "secondary_emotion": None,
                "tertiary_emotion": None,
                "keywords": [],
                "confidence": "low",
                "wellness_zone": "beradaptasi"
            }
    
    async def generate_narrative(
        self,
        user_story: str,
        detected_emotion: Dict[str, Any],
        reflection_qa: list,
        language: str = "id"
    ) -> Dict[str, Any]:
        """
        Call #2: Generate narasi reflektif MHCM
        
        Args:
            user_story: Cerita awal user
            detected_emotion: Emosi yang terdeteksi di Fase 1
            reflection_qa: 5 Q&A dari Fase 2
            language: Bahasa output (id/en)
            
        Returns:
            Dict dengan narrative dan wellness_zone
        """
        from core.llm.prompts import PromptManager
        
        prompt_manager = PromptManager()
        prompt = prompt_manager.get_narrative_generation_prompt(
            user_story=user_story,
            detected_emotion=detected_emotion,
            reflection_qa=reflection_qa,
            language=language
        )
        
        response = await self.generate_content(prompt)
        
        # Parse response
        try:
            result = self._extract_json(response)
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse narrative response: {response}")
            # Return the raw response as narrative if parsing fails
            return {
                "narrative": response,
                "wellness_zone": detected_emotion.get("wellness_zone", "beradaptasi"),
                "insights": []
            }
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response"""
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in code blocks
        import re
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, text)
        if matches:
            return json.loads(matches[0])
        
        # Try to find JSON object pattern
        json_obj_pattern = r'\{[\s\S]*\}'
        matches = re.findall(json_obj_pattern, text)
        if matches:
            return json.loads(matches[0])
        
        raise json.JSONDecodeError("No JSON found in response", text, 0)


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
