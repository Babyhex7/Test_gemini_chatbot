/**
 * =========================================
 * Routes: Chat Routes
 * =========================================
 *
 * Endpoint utama chat flow engine.
 * Semua route memerlukan autentikasi.
 */

const express = require("express");
const router = express.Router();
const { authMiddleware } = require("../middleware/auth");
const chatController = require("../controllers/chatController");

// Semua chat routes butuh autentikasi
router.use(authMiddleware);

// POST /api/chat/start - Mulai session baru + safe framing
router.post("/start", chatController.startChat);

// POST /api/chat/submit-story - Kirim cerita → detect emosi → return pertanyaan
router.post("/submit-story", chatController.submitStory);

// POST /api/chat/submit-answers - Jawab pertanyaan → scoring → narrative
router.post("/submit-answers", chatController.submitAnswers);

// GET /api/chat/:sessionId/messages - Ambil chat messages
router.get("/:sessionId/messages", chatController.getMessages);

module.exports = router;
