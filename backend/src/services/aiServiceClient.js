/**
 * =========================================
 * Service: AI Service Client (HTTP Wrapper)
 * =========================================
 *
 * Client untuk komunikasi ke AI Service (Python/FastAPI).
 * Saat ini menggunakan MOCK RESPONSES karena AI Service belum jalan.
 *
 * Nanti tinggal ganti mock dengan HTTP call ke AI_SERVICE_URL.
 * Mock ditandai dengan flag USE_MOCK di .env
 */

const { AppError } = require("../middleware/errorHandler");

// Base URL AI Service dari environment
const AI_BASE_URL = process.env.AI_SERVICE_URL || "http://localhost:8000";

// Flag untuk mock mode (default: true sampai AI Service ready)
const USE_MOCK = process.env.USE_MOCK_AI !== "false";

// =========================================
// MOCK RESPONSES
// =========================================

/**
 * Mock response untuk deteksi emosi
 * Simulasi hasil dari Gemini AI
 */
const MOCK_EMOTION_DETECTION = {
  primary: "Sad",
  secondary: "Lonely",
  tertiary: "Isolated",
  confidence: 0.85,
  reasoning:
    "[MOCK] Berdasarkan cerita user, terdeteksi perasaan kesepian dan isolasi. " +
    "User mengekspresikan perasaan terputus dari lingkungan sosialnya.",
  storySummary: "[MOCK] User merasa kesepian dan terisolasi dari lingkungan.",
};

/**
 * Mock response untuk generate narrative
 * Simulasi narrative reflektif dari Gemini
 */
const MOCK_NARRATIVE_RESPONSE = {
  narrative:
    "[MOCK] Perasaan yang kamu alami sangat wajar dan valid. " +
    "Kesepian adalah emosi yang umum dirasakan, terutama saat kita merasa " +
    "terputus dari orang-orang di sekitar kita. Penting untuk diingat bahwa " +
    "perasaan ini tidak mendefinisikan siapa dirimu. Kamu memiliki keberanian " +
    "untuk mengekspresikan perasaanmu, dan itu adalah langkah pertama yang " +
    "sangat berarti. Cobalah untuk menghubungi seseorang yang kamu percaya, " +
    "bahkan sebuah pesan singkat bisa membuka jalan untuk koneksi yang lebih dalam.",
  journeyNote:
    "[MOCK] Pola emosi menunjukkan kemungkinan recurring loneliness. " +
    "Disarankan untuk eksplorasi support system.",
};

// =========================================
// AI SERVICE METHODS
// =========================================

/**
 * Deteksi emosi dari cerita user
 * @param {Object} params
 * @param {string} params.storyText - Cerita lengkap user
 * @param {Array} params.history - History session sebelumnya
 * @returns {Promise<Object>} - { primary, secondary, tertiary, confidence, reasoning, storySummary }
 */
const detectEmotion = async ({ storyText, history = [] }) => {
  // Validasi input
  if (!storyText || storyText.trim().length === 0) {
    throw new AppError("Cerita tidak boleh kosong", 400, "VALIDATION_ERROR");
  }

  // === MOCK MODE ===
  if (USE_MOCK) {
    console.log("🤖 [MOCK] Detect emotion - menggunakan mock response");
    // Simulasi delay AI processing
    await new Promise((resolve) => setTimeout(resolve, 500));
    return { ...MOCK_EMOTION_DETECTION };
  }

  // === REAL AI SERVICE (nanti diaktifkan) ===
  try {
    const response = await fetch(`${AI_BASE_URL}/detect-emotion`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ story_text: storyText, history }),
      signal: AbortSignal.timeout(30000), // 30s timeout
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new AppError(
        `AI Service error: ${errorData.detail || response.statusText}`,
        502,
        "AI_SERVICE_ERROR",
      );
    }

    return response.json();
  } catch (error) {
    if (error instanceof AppError) throw error;

    // Network error / timeout
    throw new AppError(
      `Gagal terhubung ke AI Service: ${error.message}`,
      503,
      "AI_SERVICE_UNAVAILABLE",
    );
  }
};

/**
 * Generate narrative reflektif
 * @param {Object} params
 * @param {string} params.storyText - Cerita user
 * @param {string} params.emotionPath - "Primary.Secondary.Tertiary"
 * @param {number} params.validationScore - Skor validasi (0-100)
 * @param {Array} params.history - History session
 * @returns {Promise<Object>} - { narrative, journeyNote }
 */
const generateNarrative = async ({
  storyText,
  emotionPath,
  validationScore,
  history = [],
}) => {
  // === MOCK MODE ===
  if (USE_MOCK) {
    console.log("🤖 [MOCK] Generate narrative - menggunakan mock response");
    await new Promise((resolve) => setTimeout(resolve, 500));
    return { ...MOCK_NARRATIVE_RESPONSE };
  }

  // === REAL AI SERVICE (nanti diaktifkan) ===
  try {
    const response = await fetch(`${AI_BASE_URL}/generate-narrative`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        story_text: storyText,
        emotion_path: emotionPath,
        validation_score: validationScore,
        history,
      }),
      signal: AbortSignal.timeout(60000), // 60s timeout (narrative lebih lama)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new AppError(
        `AI Service error: ${errorData.detail || response.statusText}`,
        502,
        "AI_SERVICE_ERROR",
      );
    }

    return response.json();
  } catch (error) {
    if (error instanceof AppError) throw error;

    throw new AppError(
      `Gagal terhubung ke AI Service: ${error.message}`,
      503,
      "AI_SERVICE_UNAVAILABLE",
    );
  }
};

/**
 * Health check AI Service
 * @returns {Promise<Object>} - Status AI Service
 */
const healthCheck = async () => {
  if (USE_MOCK) {
    return { status: "mock", message: "AI Service dalam mode mock" };
  }

  try {
    const response = await fetch(`${AI_BASE_URL}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    return response.json();
  } catch (error) {
    return { status: "offline", message: error.message };
  }
};

module.exports = {
  detectEmotion,
  generateNarrative,
  healthCheck,
  USE_MOCK,
};
