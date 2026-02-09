/**
 * =========================================
 * Middleware: Error Handler
 * =========================================
 *
 * Centralized error handling untuk semua routes.
 * Handle berbagai jenis error dan return response yang konsisten.
 */

/**
 * Custom Error Class untuk Operational Errors
 * Gunakan ini untuk error yang "expected" (validation, not found, dll)
 */
class AppError extends Error {
  constructor(message, statusCode = 500, code = "ERROR") {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true; // Flag untuk membedakan dari programming errors

    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Async Handler Wrapper
 *
 * Wrap async route handlers untuk auto-catch promise rejections.
 * Tidak perlu try-catch di setiap route handler.
 *
 * Cara pakai:
 * router.get('/path', asyncHandler(async (req, res) => {
 *   const data = await someAsyncOperation();
 *   res.json(data);
 * }));
 */
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

/**
 * Not Found Middleware
 *
 * Handle route yang tidak ditemukan (404).
 * Taruh SETELAH semua routes, SEBELUM error handler.
 */
const notFoundHandler = (req, res, next) => {
  const error = new AppError(
    `Route ${req.method} ${req.originalUrl} tidak ditemukan`,
    404,
    "NOT_FOUND",
  );
  next(error);
};

/**
 * Global Error Handler Middleware
 *
 * Handle semua error dari routes dan middleware.
 * HARUS punya 4 parameter (err, req, res, next) untuk dikenali Express sebagai error handler.
 * Taruh PALING AKHIR setelah semua routes.
 */
const errorHandler = (err, req, res, next) => {
  // Log error untuk debugging (di development)
  if (process.env.NODE_ENV === "development") {
    console.error("❌ Error:", err.message);
    console.error("Stack:", err.stack);
  } else {
    // Di production, log error tanpa stack untuk security
    console.error("❌ Error:", err.message);
  }

  // Default values
  let statusCode = err.statusCode || 500;
  let message = err.message || "Terjadi kesalahan server";
  let code = err.code || "SERVER_ERROR";

  // Handle Sequelize Validation Errors
  if (err.name === "SequelizeValidationError") {
    statusCode = 400;
    code = "VALIDATION_ERROR";
    message = err.errors.map((e) => e.message).join(", ");
  }

  // Handle Sequelize Unique Constraint Errors
  if (err.name === "SequelizeUniqueConstraintError") {
    statusCode = 400;
    code = "DUPLICATE_ERROR";
    message = err.errors.map((e) => e.message).join(", ");
  }

  // Handle Sequelize Foreign Key Errors
  if (err.name === "SequelizeForeignKeyConstraintError") {
    statusCode = 400;
    code = "REFERENCE_ERROR";
    message = "Data yang direferensikan tidak ditemukan";
  }

  // Handle Sequelize Database Errors
  if (err.name === "SequelizeDatabaseError") {
    statusCode = 500;
    code = "DATABASE_ERROR";
    message =
      process.env.NODE_ENV === "development"
        ? err.message
        : "Terjadi kesalahan database";
  }

  // Handle JWT Errors (backup jika tidak di-handle di auth middleware)
  if (err.name === "JsonWebTokenError") {
    statusCode = 401;
    code = "INVALID_TOKEN";
    message = "Token tidak valid";
  }

  if (err.name === "TokenExpiredError") {
    statusCode = 401;
    code = "TOKEN_EXPIRED";
    message = "Token sudah expired";
  }

  // Build response object
  const response = {
    success: false,
    error: message,
    code,
  };

  // Di development, sertakan stack trace
  if (process.env.NODE_ENV === "development") {
    response.stack = err.stack;
  }

  // Kirim response
  res.status(statusCode).json(response);
};

module.exports = {
  AppError,
  asyncHandler,
  notFoundHandler,
  errorHandler,
};
