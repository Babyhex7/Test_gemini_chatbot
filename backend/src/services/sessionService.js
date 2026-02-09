/**
 * =========================================
 * Service: Session Service
 * =========================================
 *
 * Handle semua operasi terkait session:
 * - Buat session baru
 * - Ambil session by ID
 * - Update status/flow_state
 * - Ambil history session user
 * - Format history untuk AI Service
 */

const {
  Session,
  EmotionLog,
  QuestionAnswer,
  ChatMessage,
  FLOW_STATES,
  SESSION_STATUS,
} = require("../models");
const { AppError } = require("../middleware/errorHandler");
const { Op } = require("sequelize");

/**
 * Buat session baru untuk user
 * @param {number} userId - ID user
 * @returns {Promise<Session>} - Session baru
 */
const createSession = async (userId) => {
  const session = await Session.create({
    user_id: userId,
    flow_state: FLOW_STATES.SAFE_FRAMING,
    status: SESSION_STATUS.ACTIVE,
    started_at: new Date(),
  });

  return session;
};

/**
 * Ambil session by ID dengan relasi lengkap
 * @param {number} sessionId - ID session
 * @param {number} userId - ID user (untuk validasi ownership)
 * @returns {Promise<Session>}
 */
const getSessionById = async (sessionId, userId) => {
  const session = await Session.findOne({
    where: { id: sessionId, user_id: userId },
    include: [
      { association: "emotionLogs", order: [["created_at", "ASC"]] },
      { association: "answers", order: [["question_index", "ASC"]] },
      { association: "messages", order: [["created_at", "ASC"]] },
    ],
  });

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  return session;
};

/**
 * Update flow state session
 * @param {number} sessionId - ID session
 * @param {string} newState - State baru dari FLOW_STATES
 * @returns {Promise<Session>}
 */
const updateFlowState = async (sessionId, newState) => {
  const session = await Session.findByPk(sessionId);

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  session.flow_state = newState;
  await session.save();

  return session;
};

/**
 * Update detected emotion di session
 * @param {number} sessionId
 * @param {Object} emotion - { primary, secondary, tertiary }
 * @returns {Promise<Session>}
 */
const updateDetectedEmotion = async (sessionId, emotion) => {
  const session = await Session.findByPk(sessionId);

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  session.detected_primary = emotion.primary;
  session.detected_secondary = emotion.secondary;
  session.detected_tertiary = emotion.tertiary;
  await session.save();

  return session;
};

/**
 * Update final emotion (setelah validasi jawaban)
 * @param {number} sessionId
 * @param {Object} emotion - { primary, secondary, tertiary }
 * @returns {Promise<Session>}
 */
const updateFinalEmotion = async (sessionId, emotion) => {
  const session = await Session.findByPk(sessionId);

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  session.final_primary = emotion.primary;
  session.final_secondary = emotion.secondary;
  session.final_tertiary = emotion.tertiary;
  await session.save();

  return session;
};

/**
 * Simpan cerita user ke session
 * @param {number} sessionId
 * @param {string} storyText - Cerita lengkap
 * @param {string} storySummary - Ringkasan (opsional, max 200 char)
 * @returns {Promise<Session>}
 */
const saveStory = async (sessionId, storyText, storySummary = null) => {
  const session = await Session.findByPk(sessionId);

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  session.story_text = storyText;
  session.story_summary = storySummary || storyText.substring(0, 200); // Auto-truncate kalau ga ada summary
  await session.save();

  return session;
};

/**
 * Ambil riwayat session user (N session terakhir)
 * @param {number} userId - ID user
 * @param {number} limit - Jumlah session (default 5)
 * @returns {Promise<Array>}
 */
const getUserSessionHistory = async (userId, limit = 5) => {
  const sessions = await Session.findAll({
    where: {
      user_id: userId,
      status: SESSION_STATUS.COMPLETED,
    },
    include: [
      {
        association: "emotionLogs",
        where: { source: "validated" },
        required: false, // LEFT JOIN - tetap tampilkan session tanpa log
      },
    ],
    order: [["created_at", "DESC"]],
    limit,
  });

  return sessions;
};

/**
 * Format history untuk dikirim ke AI Service sebagai memory/context
 * @param {number} userId - ID user
 * @param {number} limit - Jumlah history (default 3)
 * @returns {Promise<Array>} - Array ringkasan session
 */
const formatHistoryForAI = async (userId, limit = 3) => {
  const sessions = await getUserSessionHistory(userId, limit);

  return sessions.map((session) => {
    const emotionLog = session.emotionLogs?.[0];

    return {
      sessionDate: session.created_at,
      storySummary: session.story_summary || "(tidak ada ringkasan)",
      emotion: emotionLog
        ? {
            primary: emotionLog.primary_emotion,
            secondary: emotionLog.secondary_emotion,
            tertiary: emotionLog.tertiary_emotion,
            confidence: emotionLog.confidence,
          }
        : null,
      journeyNote: emotionLog?.journey_note || null,
    };
  });
};

/**
 * Tandai session selesai
 * @param {number} sessionId
 * @returns {Promise<Session>}
 */
const completeSession = async (sessionId) => {
  const session = await Session.findByPk(sessionId);

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  await session.markCompleted();
  return session;
};

/**
 * Tandai session abandoned
 * @param {number} sessionId
 * @returns {Promise<Session>}
 */
const abandonSession = async (sessionId) => {
  const session = await Session.findByPk(sessionId);

  if (!session) {
    throw new AppError("Session tidak ditemukan", 404, "SESSION_NOT_FOUND");
  }

  session.status = SESSION_STATUS.ABANDONED;
  session.ended_at = new Date();
  await session.save();

  return session;
};

module.exports = {
  createSession,
  getSessionById,
  updateFlowState,
  updateDetectedEmotion,
  updateFinalEmotion,
  saveStory,
  getUserSessionHistory,
  formatHistoryForAI,
  completeSession,
  abandonSession,
};
