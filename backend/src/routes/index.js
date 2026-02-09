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

// =========================================
// PLACEHOLDER ROUTES (akan diimplementasi nanti)
// =========================================

/**
 * Session routes - /api/sessions/*
 * Handle session CRUD
 */
// router.use('/sessions', sessionRoutes);

/**
 * Chat routes - /api/chat/*
 * Handle chat flow engine
 */
// router.use('/chat', chatRoutes);

/**
 * Emotion routes - /api/emotions/*
 * Handle emotion wheel dan logs
 */
// router.use('/emotions', emotionRoutes);

/**
 * Questions routes - /api/questions/*
 * Handle reflection questions
 */
// router.use('/questions', questionRoutes);

/**
 * History routes - /api/history/*
 * Handle session history untuk memory inject
 */
// router.use('/history', historyRoutes);

module.exports = router;
