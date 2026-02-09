/**
 * =========================================
 * Controller: Session Controller
 * =========================================
 *
 * Handle request terkait session management:
 * - Buat session baru
 * - Lihat detail session
 * - Lihat history user
 * - Abandon session
 */

const sessionService = require("../services/sessionService");
const { asyncHandler, AppError } = require("../middleware/errorHandler");

/**
 * POST /api/sessions/new
 * Buat session baru untuk user yang login
 */
const createSession = asyncHandler(async (req, res) => {
  const session = await sessionService.createSession(req.userId);

  res.status(201).json({
    success: true,
    message: "Session baru berhasil dibuat",
    data: {
      sessionId: session.id,
      flowState: session.flow_state,
      status: session.status,
      startedAt: session.started_at,
    },
  });
});

/**
 * GET /api/sessions/:sessionId
 * Ambil detail session lengkap (emotion logs, answers, messages)
 */
const getSession = asyncHandler(async (req, res) => {
  const { sessionId } = req.params;
  const session = await sessionService.getSessionById(
    parseInt(sessionId),
    req.userId,
  );

  res.json({
    success: true,
    data: {
      id: session.id,
      flowState: session.flow_state,
      status: session.status,
      storyText: session.story_text,
      storySummary: session.story_summary,
      detectedEmotion: {
        primary: session.detected_primary,
        secondary: session.detected_secondary,
        tertiary: session.detected_tertiary,
      },
      finalEmotion: {
        primary: session.final_primary,
        secondary: session.final_secondary,
        tertiary: session.final_tertiary,
      },
      emotionLogs: session.emotionLogs,
      answers: session.answers,
      messages: session.messages?.map((m) => m.toChatFormat()),
      startedAt: session.started_at,
      endedAt: session.ended_at,
    },
  });
});

/**
 * GET /api/sessions/history
 * Ambil riwayat session user yang login (default 10 terakhir)
 */
const getUserHistory = asyncHandler(async (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  const sessions = await sessionService.getUserSessionHistory(
    req.userId,
    limit,
  );

  res.json({
    success: true,
    data: {
      total: sessions.length,
      sessions: sessions.map((s) => ({
        id: s.id,
        storySummary: s.story_summary,
        emotion: s.emotionLogs?.[0]
          ? {
              primary: s.emotionLogs[0].primary_emotion,
              secondary: s.emotionLogs[0].secondary_emotion,
              tertiary: s.emotionLogs[0].tertiary_emotion,
            }
          : null,
        status: s.status,
        createdAt: s.created_at,
      })),
    },
  });
});

/**
 * GET /api/sessions/history/ai
 * Ambil history yang sudah diformat untuk AI Service context
 */
const getAIHistory = asyncHandler(async (req, res) => {
  const limit = parseInt(req.query.limit) || 3;
  const history = await sessionService.formatHistoryForAI(req.userId, limit);

  res.json({
    success: true,
    data: { history },
  });
});

/**
 * PUT /api/sessions/:sessionId/abandon
 * Tandai session sebagai abandoned
 */
const abandonSession = asyncHandler(async (req, res) => {
  const { sessionId } = req.params;

  // Pastikan session milik user
  await sessionService.getSessionById(parseInt(sessionId), req.userId);
  const session = await sessionService.abandonSession(parseInt(sessionId));

  res.json({
    success: true,
    message: "Session ditandai sebagai abandoned",
    data: {
      id: session.id,
      status: session.status,
      endedAt: session.ended_at,
    },
  });
});

module.exports = {
  createSession,
  getSession,
  getUserHistory,
  getAIHistory,
  abandonSession,
};
