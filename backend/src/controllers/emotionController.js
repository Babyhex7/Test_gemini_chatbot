/**
 * =========================================
 * Controller: Emotion Controller
 * =========================================
 *
 * Handle request terkait emosi:
 * - Ambil pertanyaan refleksi by emotion path
 * - Ambil daftar primary emotions
 * - Ambil metadata/detail emosi
 * - Ambil journey emosi user
 */

const emotionService = require("../services/emotionService");
const { asyncHandler } = require("../middleware/errorHandler");

/**
 * GET /api/emotions/questions?path=Happy.Proud.Confident
 * Ambil pertanyaan refleksi berdasarkan emotion path
 */
const getQuestions = asyncHandler(async (req, res) => {
  const { path } = req.query;
  const questions = await emotionService.getReflectionQuestions(path);

  res.json({
    success: true,
    data: {
      emotionPath: path,
      total: questions.length,
      questions,
    },
  });
});

/**
 * GET /api/emotions/primaries
 * Ambil daftar semua primary emotions dari EmotionWheel
 */
const getPrimaries = asyncHandler(async (req, res) => {
  const primaries = await emotionService.getPrimaryEmotions();

  res.json({
    success: true,
    data: { primaries },
  });
});

/**
 * GET /api/emotions/:primary
 * Ambil metadata emosi (secondary + tertiary) by primary
 */
const getMetadata = asyncHandler(async (req, res) => {
  const { primary } = req.params;
  const metadata = await emotionService.getEmotionMetadata(primary);

  res.json({
    success: true,
    data: metadata,
  });
});

/**
 * GET /api/emotions/validate?primary=Happy&secondary=Proud&tertiary=Confident
 * Validasi apakah kombinasi emosi valid
 */
const validateEmotion = asyncHandler(async (req, res) => {
  const { primary, secondary, tertiary } = req.query;
  const isValid = await emotionService.validateEmotionPath(
    primary,
    secondary,
    tertiary,
  );

  res.json({
    success: true,
    data: {
      primary,
      secondary,
      tertiary,
      isValid,
    },
  });
});

/**
 * GET /api/emotions/journey (protected)
 * Ambil journey emosi user yang login
 */
const getJourney = asyncHandler(async (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  const journey = await emotionService.getUserEmotionJourney(req.userId, limit);

  res.json({
    success: true,
    data: {
      total: journey.length,
      journey,
    },
  });
});

module.exports = {
  getQuestions,
  getPrimaries,
  getMetadata,
  validateEmotion,
  getJourney,
};
