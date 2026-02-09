/**
 * =========================================
 * Routes: Auth Routes
 * =========================================
 *
 * Routes untuk autentikasi: register, login, profile.
 * Base path: /api/auth
 */

const express = require("express");
const router = express.Router();

const {
  register,
  login,
  getMe,
  updateProfile,
  changePassword,
} = require("../controllers/authController");

const { authMiddleware } = require("../middleware/auth");

// =========================================
// PUBLIC ROUTES (Tidak perlu login)
// =========================================

/**
 * POST /api/auth/register
 * Registrasi user baru
 */
router.post("/register", register);

/**
 * POST /api/auth/login
 * Login user
 */
router.post("/login", login);

// =========================================
// PROTECTED ROUTES (Perlu login)
// =========================================

/**
 * GET /api/auth/me
 * Ambil profil user yang sedang login
 */
router.get("/me", authMiddleware, getMe);

/**
 * PUT /api/auth/me
 * Update profil user
 */
router.put("/me", authMiddleware, updateProfile);

/**
 * PUT /api/auth/password
 * Ganti password
 */
router.put("/password", authMiddleware, changePassword);

module.exports = router;
