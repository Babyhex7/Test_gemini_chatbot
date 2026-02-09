/**
 * =========================================
 * Middleware: JWT Authentication
 * =========================================
 *
 * Middleware untuk verifikasi JWT token pada protected routes.
 * Mengekstrak token dari header Authorization: Bearer <token>
 */

const jwt = require("jsonwebtoken");
const { User } = require("../models");

/**
 * Middleware: Autentikasi JWT
 *
 * Cara pakai:
 * router.get('/protected', authMiddleware, (req, res) => {
 *   // req.user sudah berisi data user
 * });
 */
const authMiddleware = async (req, res, next) => {
  try {
    // Ambil token dari header Authorization
    const authHeader = req.headers.authorization;

    // Cek apakah header ada dan format valid (Bearer <token>)
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({
        success: false,
        error: "Token tidak ditemukan",
        code: "NO_TOKEN",
      });
    }

    // Ekstrak token (hilangkan "Bearer ")
    const token = authHeader.split(" ")[1];

    // Verifikasi token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Cari user di database untuk memastikan masih valid
    const user = await User.findByPk(decoded.userId);

    // Jika user tidak ditemukan (mungkin sudah dihapus)
    if (!user) {
      return res.status(401).json({
        success: false,
        error: "User tidak ditemukan",
        code: "USER_NOT_FOUND",
      });
    }

    // Simpan user di request object untuk dipakai di route handler
    req.user = user.toSafeObject();
    req.userId = user.id;

    // Lanjut ke route handler berikutnya
    next();
  } catch (error) {
    // Handle berbagai error JWT
    if (error.name === "TokenExpiredError") {
      return res.status(401).json({
        success: false,
        error: "Token sudah expired",
        code: "TOKEN_EXPIRED",
        expiredAt: error.expiredAt,
      });
    }

    if (error.name === "JsonWebTokenError") {
      return res.status(401).json({
        success: false,
        error: "Token tidak valid",
        code: "INVALID_TOKEN",
        message: error.message,
      });
    }

    if (error.name === "NotBeforeError") {
      return res.status(401).json({
        success: false,
        error: "Token belum aktif",
        code: "TOKEN_NOT_ACTIVE",
      });
    }

    // Error lainnya
    console.error("Auth middleware error:", error);
    return res.status(500).json({
      success: false,
      error: "Gagal memverifikasi token",
      code: "AUTH_ERROR",
    });
  }
};

/**
 * Middleware: Opsional Auth
 *
 * Sama seperti authMiddleware, tapi tidak error jika tidak ada token.
 * Berguna untuk endpoint yang bisa diakses guest tapi enhanced untuk logged-in user.
 */
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;

    // Jika tidak ada token, lanjut tanpa user
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      req.user = null;
      req.userId = null;
      return next();
    }

    const token = authHeader.split(" ")[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findByPk(decoded.userId);

    if (user) {
      req.user = user.toSafeObject();
      req.userId = user.id;
    } else {
      req.user = null;
      req.userId = null;
    }

    next();
  } catch (error) {
    // Untuk optional auth, abaikan error dan lanjut tanpa user
    req.user = null;
    req.userId = null;
    next();
  }
};

/**
 * Helper: Generate JWT Token
 *
 * @param {Object} user - User object dari database
 * @returns {string} JWT token
 */
const generateToken = (user) => {
  const payload = {
    userId: user.id,
    email: user.email,
    name: user.name,
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN || "7d",
    issuer: "mhcm-chatbot",
  });
};

module.exports = {
  authMiddleware,
  optionalAuth,
  generateToken,
};
