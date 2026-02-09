/**
 * =========================================
 * Routes Index - Central Router
 * =========================================
 *
 * File ini mengumpulkan semua routes dan mount ke base path masing-masing.
 * Import file ini di app.js untuk mengaktifkan semua routes.
 */

const express = require("express");
const router = express.Router();

// Import route modules
const authRoutes = require("./authRoutes");
const sessionRoutes = require("./sessionRoutes");
const emotionRoutes = require("./emotionRoutes");
const chatRoutes = require("./chatRoutes");

// =========================================
// MOUNT ROUTES
// =========================================

/**
 * Root API endpoint - /api
 * Info tentang available routes
 */
router.get("/", (req, res) => {
  res.json({
    success: true,
    message: "MHCM Chatbot API v1.0",
    version: "1.0.0",
    endpoints: {
      health: "/api/health",
      auth: {
        register: "POST /api/auth/register",
        login: "POST /api/auth/login",
        me: "GET /api/auth/me (protected)",
        updateProfile: "PUT /api/auth/me (protected)",
        changePassword: "PUT /api/auth/password (protected)",
      },
      sessions: {
        create: "POST /api/sessions/new (protected)",
        detail: "GET /api/sessions/:sessionId (protected)",
        history: "GET /api/sessions/history (protected)",
        historyAI: "GET /api/sessions/history/ai (protected)",
        abandon: "PUT /api/sessions/:sessionId/abandon (protected)",
      },
      emotions: {
        primaries: "GET /api/emotions/primaries",
        questions:
          "GET /api/emotions/questions?path=Primary.Secondary.Tertiary",
        validate:
          "GET /api/emotions/validate?primary=...&secondary=...&tertiary=...",
        metadata: "GET /api/emotions/:primary",
        journey: "GET /api/emotions/journey (protected)",
      },
      chat: {
        start: "POST /api/chat/start (protected)",
        submitStory: "POST /api/chat/submit-story (protected)",
        submitAnswers: "POST /api/chat/submit-answers (protected)",
        messages: "GET /api/chat/:sessionId/messages (protected)",
      },
    },
  });
});

/**
 * Auth routes - /api/auth/*
 * Handle registrasi, login, dan profil user
 */
router.use("/auth", authRoutes);

/**
 * Health check endpoint - /api/health
 * Untuk monitoring server status
 */
router.get("/health", (req, res) => {
  res.json({
    success: true,
    status: "OK",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || "development",
  });
});

/**
 * Session routes - /api/sessions/*
 * Handle session CRUD dan history
 */
router.use("/sessions", sessionRoutes);

/**
 * Emotion routes - /api/emotions/*
 * Handle emotion wheel, pertanyaan refleksi, dan journey
 */
router.use("/emotions", emotionRoutes);

/**
 * Chat routes - /api/chat/*
 * Handle chat flow engine (start → story → answers → narrative)
 */
router.use("/chat", chatRoutes);

module.exports = router;
