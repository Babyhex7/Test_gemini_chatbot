/**
 * =========================================
 * Routes: Session Routes
 * =========================================
 *
 * Semua endpoint terkait session management.
 * Semua route di sini memerlukan autentikasi (authMiddleware).
 */

const express = require("express");
const router = express.Router();
const { authMiddleware } = require("../middleware/auth");
const sessionController = require("../controllers/sessionController");

// Semua route butuh autentikasi
router.use(authMiddleware);

// POST /api/sessions/new - Buat session baru
router.post("/new", sessionController.createSession);

// GET /api/sessions/history - Riwayat session user
router.get("/history", sessionController.getUserHistory);

// GET /api/sessions/history/ai - History format untuk AI
router.get("/history/ai", sessionController.getAIHistory);

// GET /api/sessions/:sessionId - Detail session
router.get("/:sessionId", sessionController.getSession);

// PUT /api/sessions/:sessionId/abandon - Abandon session
router.put("/:sessionId/abandon", sessionController.abandonSession);

module.exports = router;
