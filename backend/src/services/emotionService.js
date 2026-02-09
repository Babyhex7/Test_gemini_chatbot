/**
 * =========================================
 * Service: Emotion Service
 * =========================================
 *
 * Handle semua operasi terkait emosi:
 * - Load reflection questions berdasarkan emotion path
 * - Ambil metadata emosi dari EmotionWheel
 * - Format data emosi untuk AI Service
 * - Validasi emotion path
 */

const { EmotionWheel, ReflectionQuestion, EmotionLog } = require("../models");
const { AppError } = require("../middleware/errorHandler");
const { Op } = require("sequelize");

/**
 * Ambil pertanyaan refleksi berdasarkan emotion path
 * @param {string} emotionPath - Format "Primary.Secondary.Tertiary"
 * @returns {Promise<Array>} - Array pertanyaan berurutan
 */
const getReflectionQuestions = async (emotionPath) => {
  if (!emotionPath) {
    throw new AppError("Emotion path wajib diisi", 400, "VALIDATION_ERROR");
  }

  const questions = await ReflectionQuestion.getByEmotionKey(emotionPath);

  if (!questions || questions.length === 0) {
    throw new AppError(
      `Pertanyaan untuk emotion path "${emotionPath}" tidak ditemukan`,
      404,
      "QUESTIONS_NOT_FOUND",
    );
  }

  // Format untuk response
  return questions.map((q) => q.toQuestionFormat());
};

/**
 * Validasi apakah emotion path valid di EmotionWheel
 * @param {string} primary
 * @param {string} secondary
 * @param {string} tertiary
 * @returns {Promise<boolean>}
 */
const validateEmotionPath = async (primary, secondary, tertiary) => {
  const isValid = await EmotionWheel.isValidCombination(
    primary,
    secondary,
    tertiary,
  );
  return isValid;
};

/**
 * Ambil semua primary emotions dari EmotionWheel
 * @returns {Promise<Array>} - Daftar primary emotions
 */
const getPrimaryEmotions = async () => {
  return EmotionWheel.getPrimaryEmotions();
};

/**
 * Ambil metadata emosi dari EmotionWheel
 * Termasuk deskripsi dan child emotions
 * @param {string} primary - Primary emotion
 * @returns {Promise<Array>} - Metadata emosi
 */
const getEmotionMetadata = async (primary) => {
  const emotions = await EmotionWheel.findAll({
    where: { primary_emotion: primary },
    order: [
      ["secondary_emotion", "ASC"],
      ["tertiary_emotion", "ASC"],
    ],
  });

  if (!emotions || emotions.length === 0) {
    throw new AppError(
      `Emotion "${primary}" tidak ditemukan`,
      404,
      "EMOTION_NOT_FOUND",
    );
  }

  // Group by secondary
  const grouped = {};
  emotions.forEach((e) => {
    const sec = e.secondary_emotion;
    if (!grouped[sec]) {
      grouped[sec] = { secondary: sec, tertiaries: [] };
    }
    if (e.tertiary_emotion) {
      grouped[sec].tertiaries.push(e.tertiary_emotion);
    }
  });

  return {
    primary,
    secondaries: Object.values(grouped),
  };
};

/**
 * Simpan hasil deteksi emosi ke EmotionLog
 * @param {Object} params
 * @param {number} params.sessionId
 * @param {number} params.userId
 * @param {string} params.primary
 * @param {string} params.secondary
 * @param {string} params.tertiary
 * @param {number} params.confidence
 * @param {string} params.source - 'ai_detect' atau 'validated'
 * @returns {Promise<EmotionLog>}
 */
const saveEmotionLog = async ({
  sessionId,
  userId,
  primary,
  secondary,
  tertiary,
  confidence = null,
  source = "ai_detect",
}) => {
  const log = await EmotionLog.create({
    session_id: sessionId,
    user_id: userId,
    primary_emotion: primary,
    secondary_emotion: secondary,
    tertiary_emotion: tertiary,
    confidence,
    source,
    detected_at: new Date(),
  });

  return log;
};

/**
 * Update emotion log dengan narrative dan skor validasi
 * @param {number} emotionLogId
 * @param {Object} data - { narrative, journeyNote, validationScore }
 * @returns {Promise<EmotionLog>}
 */
const updateEmotionLog = async (emotionLogId, data) => {
  const log = await EmotionLog.findByPk(emotionLogId);

  if (!log) {
    throw new AppError(
      "Emotion log tidak ditemukan",
      404,
      "EMOTION_LOG_NOT_FOUND",
    );
  }

  if (data.narrative !== undefined) log.narrative = data.narrative;
  if (data.journeyNote !== undefined) log.journey_note = data.journeyNote;
  if (data.validationScore !== undefined)
    log.validation_score_tertiary = data.validationScore;
  if (data.source !== undefined) log.source = data.source;

  await log.save();
  return log;
};

/**
 * Format data emosi untuk dikirim ke AI Service
 * @param {string} emotionPath - "Primary.Secondary.Tertiary"
 * @returns {Promise<Object>} - Metadata lengkap untuk AI
 */
const formatEmotionForAI = async (emotionPath) => {
  const [primary, secondary, tertiary] = emotionPath.split(".");

  return {
    emotionPath,
    primary: primary || null,
    secondary: secondary || null,
    tertiary: tertiary || null,
    isValid: await validateEmotionPath(primary, secondary, tertiary),
  };
};

/**
 * Ambil journey emosi user (semua emotion log)
 * @param {number} userId
 * @param {number} limit
 * @returns {Promise<Array>}
 */
const getUserEmotionJourney = async (userId, limit = 10) => {
  const logs = await EmotionLog.findAll({
    where: { user_id: userId },
    order: [["detected_at", "DESC"]],
    limit,
  });

  return logs.map((log) => log.toHistorySummary());
};

module.exports = {
  getReflectionQuestions,
  validateEmotionPath,
  getPrimaryEmotions,
  getEmotionMetadata,
  saveEmotionLog,
  updateEmotionLog,
  formatEmotionForAI,
  getUserEmotionJourney,
};
