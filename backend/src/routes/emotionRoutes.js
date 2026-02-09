/**
 * =========================================
 * Routes: Emotion Routes
 * =========================================
 *
 * Endpoint terkait emosi dan pertanyaan refleksi.
 * Beberapa route public, beberapa butuh auth.
 */

const express = require("express");
const router = express.Router();
const { authMiddleware } = require("../middleware/auth");
const emotionController = require("../controllers/emotionController");

// === PUBLIC ROUTES ===

// GET /api/emotions/primaries - Daftar primary emotions
router.get("/primaries", emotionController.getPrimaries);

// GET /api/emotions/questions?path=Happy.Proud.Confident - Pertanyaan refleksi
router.get("/questions", emotionController.getQuestions);

// GET /api/emotions/validate?primary=...&secondary=...&tertiary=... - Validasi emosi
router.get("/validate", emotionController.validateEmotion);

// === PROTECTED ROUTES ===

// GET /api/emotions/journey - Journey emosi user (butuh login)
// PENTING: route ini harus SEBELUM /:primary agar tidak tertangkap sebagai param
router.get("/journey", authMiddleware, emotionController.getJourney);

// GET /api/emotions/:primary - Metadata emosi by primary (harus paling bawah)
router.get("/:primary", emotionController.getMetadata);

module.exports = router;
