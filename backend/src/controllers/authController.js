/**
 * =========================================
 * Controller: Auth Controller
 * =========================================
 *
 * Handle autentikasi user: register, login, profile.
 * Password otomatis di-hash via User model hooks.
 */

const { User } = require("../models");
const { generateToken } = require("../middleware/auth");
const { AppError, asyncHandler } = require("../middleware/errorHandler");

/**
 * POST /api/auth/register
 *
 * Registrasi user baru.
 * Body: { name, email, password }
 * Response: { success, user, token }
 */
const register = asyncHandler(async (req, res) => {
  const { name, email, password } = req.body;

  // Validasi input
  if (!name || !email || !password) {
    throw new AppError(
      "Nama, email, dan password wajib diisi",
      400,
      "VALIDATION_ERROR",
    );
  }

  // Validasi panjang password
  if (password.length < 6) {
    throw new AppError("Password minimal 6 karakter", 400, "VALIDATION_ERROR");
  }

  // Cek apakah email sudah terdaftar
  const existingUser = await User.findOne({ where: { email } });
  if (existingUser) {
    throw new AppError("Email sudah terdaftar", 400, "DUPLICATE_EMAIL");
  }

  // Buat user baru (password otomatis di-hash via beforeCreate hook)
  const user = await User.create({ name, email, password });

  // Generate JWT token
  const token = generateToken(user);

  // Return response tanpa password
  res.status(201).json({
    success: true,
    message: "Registrasi berhasil",
    user: user.toSafeObject(),
    token,
  });
});

/**
 * POST /api/auth/login
 *
 * Login user dengan email dan password.
 * Body: { email, password }
 * Response: { success, user, token }
 */
const login = asyncHandler(async (req, res) => {
  const { email, password } = req.body;

  // Validasi input
  if (!email || !password) {
    throw new AppError(
      "Email dan password wajib diisi",
      400,
      "VALIDATION_ERROR",
    );
  }

  // Cari user berdasarkan email
  const user = await User.findOne({ where: { email } });

  // Jika user tidak ditemukan
  if (!user) {
    throw new AppError("Email atau password salah", 401, "INVALID_CREDENTIALS");
  }

  // Verifikasi password
  const isPasswordValid = await user.comparePassword(password);
  if (!isPasswordValid) {
    throw new AppError("Email atau password salah", 401, "INVALID_CREDENTIALS");
  }

  // Generate JWT token
  const token = generateToken(user);

  // Return response
  res.json({
    success: true,
    message: "Login berhasil",
    user: user.toSafeObject(),
    token,
  });
});

/**
 * GET /api/auth/me
 *
 * Ambil data user yang sedang login.
 * Memerlukan autentikasi (authMiddleware).
 * Response: { success, user }
 */
const getMe = asyncHandler(async (req, res) => {
  // req.user sudah di-set oleh authMiddleware
  res.json({
    success: true,
    user: req.user,
  });
});

/**
 * PUT /api/auth/me
 *
 * Update profil user yang sedang login.
 * Body: { name } (password update terpisah untuk security)
 * Response: { success, user }
 */
const updateProfile = asyncHandler(async (req, res) => {
  const { name } = req.body;

  // Cari user
  const user = await User.findByPk(req.userId);

  if (!user) {
    throw new AppError("User tidak ditemukan", 404, "USER_NOT_FOUND");
  }

  // Update hanya jika ada perubahan
  if (name) {
    user.name = name;
  }

  await user.save();

  res.json({
    success: true,
    message: "Profil berhasil diperbarui",
    user: user.toSafeObject(),
  });
});

/**
 * PUT /api/auth/password
 *
 * Ganti password user yang sedang login.
 * Body: { currentPassword, newPassword }
 * Response: { success, message }
 */
const changePassword = asyncHandler(async (req, res) => {
  const { currentPassword, newPassword } = req.body;

  // Validasi input
  if (!currentPassword || !newPassword) {
    throw new AppError(
      "Password lama dan baru wajib diisi",
      400,
      "VALIDATION_ERROR",
    );
  }

  if (newPassword.length < 6) {
    throw new AppError(
      "Password baru minimal 6 karakter",
      400,
      "VALIDATION_ERROR",
    );
  }

  // Cari user
  const user = await User.findByPk(req.userId);

  if (!user) {
    throw new AppError("User tidak ditemukan", 404, "USER_NOT_FOUND");
  }

  // Verifikasi password lama
  const isCurrentPasswordValid = await user.comparePassword(currentPassword);
  if (!isCurrentPasswordValid) {
    throw new AppError("Password lama salah", 401, "INVALID_PASSWORD");
  }

  // Update password (otomatis di-hash via beforeUpdate hook)
  user.password = newPassword;
  await user.save();

  res.json({
    success: true,
    message: "Password berhasil diubah",
  });
});

module.exports = {
  register,
  login,
  getMe,
  updateProfile,
  changePassword,
};
