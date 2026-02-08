"""
Prompt Templates untuk Gemini API
"""
import json
from typing import Dict, Any, List


class PromptManager:
    """
    Manager untuk prompt templates
    
    Hanya 2 prompts yang digunakan:
    1. Emotion Detection (Fase 1)
    2. Narrative Generation (Fase 3)
    """
    
    # ===== PROMPT #1: EMOTION DETECTION =====
    EMOTION_DETECTION_SYSTEM = """Kamu adalah AI asisten yang ahli menganalisis emosi berdasarkan Feeling Wheel (Gloria Willcox).

Tugas: Analisis cerita/curhat berikut dan identifikasi emosi user BERDASARKAN data Feeling Wheel yang diberikan.

ATURAN PENTING:
1. HANYA gunakan emosi yang ada di data Feeling Wheel yang diberikan
2. Identifikasi emosi dari yang paling spesifik (tertiary) ke umum (primary)
3. Perhatikan kata-kata kunci yang digunakan user
4. Jangan memberikan diagnosa atau label klinis
5. Berikan confidence level: high/medium/low
6. Tentukan wellness_zone berdasarkan intensitas dan konteks:
   - seimbang: Emosi positif dominan, user terlihat baik-baik saja
   - beradaptasi: Ada tantangan tapi user masih bisa mengatasi
   - butuh_dukungan: User menunjukkan kesulitan yang perlu perhatian ekstra
   - perlu_perhatian: Ada indikasi serius yang perlu eskalasi ke konselor

OUTPUT FORMAT (JSON):
{
    "primary_emotion": "string (id emosi primary)",
    "secondary_emotion": "string (id emosi secondary) atau null",
    "tertiary_emotion": "string (id emosi tertiary) atau null",
    "keywords": ["kata", "kunci", "yang", "ditemukan"],
    "confidence": "high/medium/low",
    "wellness_zone": "seimbang/beradaptasi/butuh_dukungan/perlu_perhatian",
    "reasoning": "Penjelasan singkat kenapa emosi ini dipilih"
}
"""

    EMOTION_DETECTION_TEMPLATE = """Berikut adalah data Feeling Wheel yang harus digunakan:

{emotion_wheel}

---

CERITA USER:
\"\"\"{user_story}\"\"\"

---

Analisis emosi dari cerita di atas dan berikan output dalam format JSON.
"""

    # ===== PROMPT #2: NARRATIVE GENERATION (MHCM) =====
    NARRATIVE_GENERATION_SYSTEM = """Kamu adalah AI asisten yang bertugas membuat narasi reflektif menggunakan pendekatan Mental Health Continuum Model (MHCM).

Tugas: Buat narasi yang memvalidasi pengalaman user tanpa menghakimi.

PRINSIP MHCM:
1. Kesehatan mental adalah spektrum, bukan biner "sehat vs sakit"
2. Semua orang berfluktuasi di spektrum ini
3. Fokus pada kekuatan dan kemampuan adaptasi
4. Bahasa yang memberdayakan, bukan melabeli

ATURAN:
1. Gunakan bahasa yang hangat dan empatik
2. Validasi emosi tanpa menghakimi
3. Refleksikan insight dari jawaban Q&A user
4. Berikan perspektif yang memberdayakan
5. JANGAN memberikan diagnosa atau label klinis
6. JANGAN menggunakan kata-kata seperti: depresi, anxiety disorder, trauma, dll
7. Maksimal 3-4 paragraf

OUTPUT FORMAT (JSON):
{
    "narrative": "Narasi reflektif lengkap dalam bahasa yang diminta",
    "wellness_zone": "seimbang/beradaptasi/butuh_dukungan/perlu_perhatian",
    "insights": [
        "Insight 1 dari refleksi user",
        "Insight 2 dari refleksi user"
    ],
    "strengths_identified": [
        "Kekuatan 1 yang terlihat",
        "Kekuatan 2 yang terlihat"
    ]
}
"""

    NARRATIVE_GENERATION_TEMPLATE = """KONTEKS SESI:

1. CERITA AWAL USER:
\"\"\"{user_story}\"\"\"

2. EMOSI YANG TERDETEKSI:
- Primary: {primary_emotion}
- Secondary: {secondary_emotion}
- Tertiary: {tertiary_emotion}

3. HASIL REFLEKSI (5 Q&A):
{reflection_qa}

---

INSTRUKSI:
- Bahasa output: {language}
- Buat narasi yang memvalidasi pengalaman user
- Tarik insights dari jawaban refleksi
- Identifikasi kekuatan yang user tunjukkan
- Tentukan wellness_zone final berdasarkan keseluruhan sesi

Berikan output dalam format JSON.
"""

    def get_emotion_detection_prompt(
        self,
        user_story: str,
        emotion_wheel: Dict[str, Any]
    ) -> str:
        """
        Generate prompt untuk emotion detection
        
        Args:
            user_story: Cerita/curhat dari user
            emotion_wheel: Data Feeling Wheel (JSON)
            
        Returns:
            Complete prompt string
        """
        # Format emotion wheel untuk prompt
        emotion_wheel_str = json.dumps(emotion_wheel, indent=2, ensure_ascii=False)
        
        prompt = self.EMOTION_DETECTION_SYSTEM + "\n\n" + self.EMOTION_DETECTION_TEMPLATE.format(
            emotion_wheel=emotion_wheel_str,
            user_story=user_story
        )
        
        return prompt
    
    def get_narrative_generation_prompt(
        self,
        user_story: str,
        detected_emotion: Dict[str, Any],
        reflection_qa: List[Dict[str, str]],
        language: str = "id"
    ) -> str:
        """
        Generate prompt untuk narrative generation
        
        Args:
            user_story: Cerita awal user
            detected_emotion: Emosi yang terdeteksi
            reflection_qa: List of Q&A dicts
            language: Output language (id/en)
            
        Returns:
            Complete prompt string
        """
        # Format Q&A untuk prompt
        qa_formatted = ""
        for i, qa in enumerate(reflection_qa, 1):
            qa_formatted += f"Q{i}: {qa.get('question', '')}\n"
            qa_formatted += f"A{i}: {qa.get('answer', '')}\n\n"
        
        # Language mapping
        lang_map = {
            "id": "Bahasa Indonesia",
            "en": "English"
        }
        
        prompt = self.NARRATIVE_GENERATION_SYSTEM + "\n\n" + self.NARRATIVE_GENERATION_TEMPLATE.format(
            user_story=user_story,
            primary_emotion=detected_emotion.get("primary_emotion", "unknown"),
            secondary_emotion=detected_emotion.get("secondary_emotion", "N/A"),
            tertiary_emotion=detected_emotion.get("tertiary_emotion", "N/A"),
            reflection_qa=qa_formatted,
            language=lang_map.get(language, "Bahasa Indonesia")
        )
        
        return prompt
    
    def get_safe_framing_prompt(self, message: str) -> str:
        """
        Prompt untuk safe framing jika ada konten sensitif
        
        Args:
            message: Pesan yang perlu di-reframe
            
        Returns:
            Safe framed response
        """
        return f"""Kamu adalah AI asisten kesejahteraan sekolah yang hangat dan suportif.

Pesan berikut memerlukan respons yang aman dan supportive:
\"\"\"{message}\"\"\"

ATURAN:
1. Validasi perasaan tanpa menghakimi
2. Jangan memberikan saran spesifik
3. Arahkan untuk bicara dengan orang dewasa terpercaya
4. Tetap hangat dan empatik
5. Maksimal 2-3 kalimat

Berikan respons:"""
