/**
 * =========================================
 * Controller: Chat Flow Controller
 * =========================================
 *
 * Handle alur percakapan utama chatbot:
 *
 * FLOW STATE MACHINE:
 * SAFE_FRAMING → STORYTELLING → STORY_TOLD → VALIDATE_EMOTION → NARRATIVE → COMPLETED
 *
 * Endpoint utama:
 * - POST /api/chat/start          → Mulai session baru + safe framing
 * - POST /api/chat/submit-story   → User kirim cerita → AI detect emosi → return pertanyaan
 * - POST /api/chat/submit-answers → User jawab pertanyaan → AI generate narrative
 */

const sessionService = require("../services/sessionService");
const emotionService = require("../services/emotionService");
const aiServiceClient = require("../services/aiServiceClient");
const {
  Session,
  ChatMessage,
  QuestionAnswer,
  FLOW_STATES,
  MESSAGE_TYPE,
} = require("../models");
const { asyncHandler, AppError } = require("../middleware/errorHandler");

// =========================================
// SAFE FRAMING MESSAGES (template)
// =========================================
const SAFE_FRAMING_MESSAGE =
  "Halo! Selamat datang di ruang aman ini. 🌿\n\n" +
  "Di sini, kamu bebas bercerita tentang apa yang sedang kamu rasakan. " +
  "Tidak ada jawaban yang salah, dan semua perasaanmu valid.\n\n" +
  "Silakan ceritakan apa yang sedang kamu alami atau rasakan saat ini. " +
  "Kamu bisa menulis sebebas dan sejujur yang kamu mau.";

// =========================================
// CHAT FLOW ENDPOINTS
// =========================================

/**
 * POST /api/chat/start
 * Mulai session baru dan tampilkan safe framing
 *
 * Response: session info + safe framing message
 */
const startChat = asyncHandler(async (req, res) => {
  // Buat session baru
  const session = await sessionService.createSession(req.userId);

  // Simpan safe framing sebagai bot message
  await ChatMessage.addBotMessage(
    session.id,
    SAFE_FRAMING_MESSAGE,
    MESSAGE_TYPE.TEXT,
    { flowState: FLOW_STATES.SAFE_FRAMING },
  );

  // Update flow state ke STORYTELLING (siap terima cerita)
  await sessionService.updateFlowState(session.id, FLOW_STATES.STORYTELLING);

  res.status(201).json({
    success: true,
    message: "Session dimulai",
    data: {
      sessionId: session.id,
      flowState: FLOW_STATES.STORYTELLING,
      botMessage: SAFE_FRAMING_MESSAGE,
      aiMode: aiServiceClient.USE_MOCK ? "mock" : "live",
    },
  });
});

/**
 * POST /api/chat/submit-story
 * User kirim cerita → AI deteksi emosi → return pertanyaan validasi
 *
 * Body: { sessionId, storyText }
 * Response: detected emotion + pertanyaan ABCD
 *
 * Flow: STORYTELLING → STORY_TOLD → VALIDATE_EMOTION
 */
const submitStory = asyncHandler(async (req, res) => {
  const { sessionId, storyText } = req.body;

  // Validasi input
  if (!sessionId || !storyText) {
    throw new AppError(
      "sessionId dan storyText wajib diisi",
      400,
      "VALIDATION_ERROR",
    );
  }

  if (storyText.trim().length < 10) {
    throw new AppError(
      "Cerita terlalu pendek, minimal 10 karakter",
      400,
      "VALIDATION_ERROR",
    );
  }

  // Ambil session dan validasi ownership
  const session = await sessionService.getSessionById(sessionId, req.userId);

  // Cek flow state - harus STORYTELLING
  if (session.flow_state !== FLOW_STATES.STORYTELLING) {
    throw new AppError(
      `Flow state tidak valid. Expected: STORYTELLING, Got: ${session.flow_state}`,
      400,
      "INVALID_FLOW_STATE",
    );
  }

  // 1. Simpan cerita user ke session (summary sementara = truncate 200 char)
  await sessionService.saveStory(session.id, storyText);

  // Simpan cerita sebagai chat message
  await ChatMessage.addUserMessage(session.id, storyText, MESSAGE_TYPE.STORY);

  // Update flow ke STORY_TOLD
  await sessionService.updateFlowState(session.id, FLOW_STATES.STORY_TOLD);

  // 2. Ambil history untuk context AI
  const history = await sessionService.formatHistoryForAI(req.userId, 3);

  // 3. Kirim ke AI Service untuk deteksi emosi
  const aiResult = await aiServiceClient.detectEmotion({
    storyText,
    history,
  });

  // 4. Simpan detected emotion ke session
  await sessionService.updateDetectedEmotion(session.id, {
    primary: aiResult.primary,
    secondary: aiResult.secondary,
    tertiary: aiResult.tertiary,
  });

  // Update story_summary dengan versi AI (lebih akurat daripada truncate)
  if (aiResult.storySummary) {
    await sessionService.saveStory(
      session.id,
      storyText,
      aiResult.storySummary,
    );
  }

  // 5. Simpan emotion log (source: ai_detect)
  const emotionLog = await emotionService.saveEmotionLog({
    sessionId: session.id,
    userId: req.userId,
    primary: aiResult.primary,
    secondary: aiResult.secondary,
    tertiary: aiResult.tertiary,
    confidence: aiResult.confidence,
    source: "ai_detect",
  });

  // 6. Ambil pertanyaan refleksi berdasarkan emotion path
  const emotionPath = `${aiResult.primary}.${aiResult.secondary}.${aiResult.tertiary}`;
  let questions = [];

  try {
    questions = await emotionService.getReflectionQuestions(emotionPath);
  } catch (error) {
    // Kalau pertanyaan belum ada untuk emotion path ini, return pesan
    console.warn(
      `⚠️ Pertanyaan untuk ${emotionPath} belum tersedia:`,
      error.message,
    );
  }

  // 7. Simpan bot message (emotion detection result + questions)
  const botMessage =
    `Terima kasih sudah bercerita. Berdasarkan ceritamu, saya mendeteksi bahwa ` +
    `kamu mungkin merasakan **${aiResult.primary}** — khususnya **${aiResult.secondary}** ` +
    `(${aiResult.tertiary}).` +
    (questions.length > 0
      ? `\n\nUntuk memastikan, mari jawab ${questions.length} pertanyaan refleksi berikut:`
      : "\n\n(Pertanyaan refleksi belum tersedia untuk emosi ini)");

  await ChatMessage.addBotMessage(session.id, botMessage, MESSAGE_TYPE.TEXT, {
    emotionDetected: {
      primary: aiResult.primary,
      secondary: aiResult.secondary,
      tertiary: aiResult.tertiary,
      confidence: aiResult.confidence,
    },
  });

  // Simpan pertanyaan sebagai bot messages
  for (const q of questions) {
    await ChatMessage.addBotMessage(
      session.id,
      q.questionText,
      MESSAGE_TYPE.QUESTION,
      { questionId: q.id, options: q.options, questionIndex: q.questionIndex },
    );
  }

  // 8. Update flow state ke VALIDATE_EMOTION
  await sessionService.updateFlowState(
    session.id,
    FLOW_STATES.VALIDATE_EMOTION,
  );

  res.json({
    success: true,
    message: "Emosi berhasil dideteksi",
    data: {
      sessionId: session.id,
      flowState: FLOW_STATES.VALIDATE_EMOTION,
      emotion: {
        primary: aiResult.primary,
        secondary: aiResult.secondary,
        tertiary: aiResult.tertiary,
        confidence: aiResult.confidence,
        reasoning: aiResult.reasoning,
      },
      emotionLogId: emotionLog.id,
      questions,
      totalQuestions: questions.length,
    },
  });
});

/**
 * POST /api/chat/submit-answers
 * User jawab pertanyaan → scoring → AI generate narrative
 *
 * Body: { sessionId, answers: [{ questionId, userAnswer }] }
 * Response: skor validasi + narrative reflektif
 *
 * Flow: VALIDATE_EMOTION → NARRATIVE → COMPLETED
 */
const submitAnswers = asyncHandler(async (req, res) => {
  const { sessionId, answers } = req.body;

  // Validasi input
  if (!sessionId || !answers || !Array.isArray(answers)) {
    throw new AppError(
      "sessionId dan answers (array) wajib diisi",
      400,
      "VALIDATION_ERROR",
    );
  }

  // Ambil session dan validasi ownership
  const session = await sessionService.getSessionById(sessionId, req.userId);

  // Cek flow state - harus VALIDATE_EMOTION
  if (session.flow_state !== FLOW_STATES.VALIDATE_EMOTION) {
    throw new AppError(
      `Flow state tidak valid. Expected: VALIDATE_EMOTION, Got: ${session.flow_state}`,
      400,
      "INVALID_FLOW_STATE",
    );
  }

  // 1. Hitung emotion key dari session
  const emotionKey = session.getEmotionKey();

  if (!emotionKey) {
    throw new AppError(
      "Emotion belum terdeteksi untuk session ini",
      400,
      "NO_EMOTION_DETECTED",
    );
  }

  // 2. Simpan jawaban dan hitung skor
  const scoreResult = await QuestionAnswer.submitAnswers(
    session.id,
    emotionKey,
    answers,
  );

  // Simpan jawaban sebagai chat messages
  for (const answer of answers) {
    await ChatMessage.addUserMessage(
      session.id,
      `Jawaban: ${answer.userAnswer}`,
      MESSAGE_TYPE.ANSWER,
      { questionId: answer.questionId, answer: answer.userAnswer },
    );
  }

  // 3. Tentukan final emotion berdasarkan skor
  // Jika skor >= 60% (3/5 benar), emosi AI dikonfirmasi
  const detected = {
    primary: session.detected_primary,
    secondary: session.detected_secondary,
    tertiary: session.detected_tertiary,
  };

  if (scoreResult.passed) {
    // Emosi dikonfirmasi — final = detected
    await sessionService.updateFinalEmotion(session.id, detected);
  } else {
    // Emosi tidak dikonfirmasi — tetap pakai detected tapi bisa di-flag
    await sessionService.updateFinalEmotion(session.id, detected);
    // TODO: Nanti bisa tambah flow untuk re-detect atau user pilih sendiri
  }

  // Update flow ke NARRATIVE
  await sessionService.updateFlowState(session.id, FLOW_STATES.NARRATIVE);

  // 4. Ambil history untuk AI context
  const history = await sessionService.formatHistoryForAI(req.userId, 3);

  // 5. Generate narrative reflektif via AI
  const narrativeResult = await aiServiceClient.generateNarrative({
    storyText: session.story_text,
    emotionPath: emotionKey,
    validationScore: scoreResult.score,
    history,
  });

  // 6. Update emotion log dengan narrative + skor
  const emotionLog = session.emotionLogs?.[0];
  if (emotionLog) {
    await emotionService.updateEmotionLog(emotionLog.id, {
      narrative: narrativeResult.narrative,
      journeyNote: narrativeResult.journeyNote,
      validationScore: scoreResult.correct,
      source: "validated",
    });
  }

  // 7. Simpan narrative sebagai bot message
  await ChatMessage.addBotMessage(
    session.id,
    narrativeResult.narrative,
    MESSAGE_TYPE.NARRATIVE,
    {
      emotionPath: emotionKey,
      validationScore: scoreResult.score,
      passed: scoreResult.passed,
    },
  );

  // 8. Tandai session selesai
  await sessionService.completeSession(session.id);

  res.json({
    success: true,
    message: "Narrative berhasil digenerate",
    data: {
      sessionId: session.id,
      flowState: FLOW_STATES.COMPLETED,
      validation: {
        total: scoreResult.total,
        correct: scoreResult.correct,
        score: scoreResult.score,
        passed: scoreResult.passed,
      },
      finalEmotion: {
        path: emotionKey,
        primary: detected.primary,
        secondary: detected.secondary,
        tertiary: detected.tertiary,
      },
      narrative: narrativeResult.narrative,
      journeyNote: narrativeResult.journeyNote,
    },
  });
});

/**
 * GET /api/chat/:sessionId/messages
 * Ambil semua chat messages dalam session
 */
const getMessages = asyncHandler(async (req, res) => {
  const { sessionId } = req.params;

  // Validasi ownership
  await sessionService.getSessionById(parseInt(sessionId), req.userId);

  const messages = await ChatMessage.getBySession(parseInt(sessionId));

  res.json({
    success: true,
    data: {
      sessionId: parseInt(sessionId),
      total: messages.length,
      messages: messages.map((m) => m.toChatFormat()),
    },
  });
});

module.exports = {
  startChat,
  submitStory,
  submitAnswers,
  getMessages,
};
