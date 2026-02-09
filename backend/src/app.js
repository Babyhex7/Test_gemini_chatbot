/**
 * =========================================
 * MHCM Chatbot - Express App
 * =========================================
 *
 * Main Express application setup.
 * Semua middleware dan routes dikonfigurasi di sini.
 */

require("dotenv").config();
const express = require("express");
const cors = require("cors");

// Import routes
const routes = require("./routes");

// Import error handlers
const { notFoundHandler, errorHandler } = require("./middleware/errorHandler");

// Buat Express app
const app = express();

// =========================================
// MIDDLEWARE SETUP
// =========================================

/**
 * CORS Configuration
 * Izinkan request dari frontend (localhost:3000)
 */
app.use(
  cors({
    origin: process.env.CORS_ORIGIN || "http://localhost:3000",
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true, // Izinkan kirim cookies
  }),
);

/**
 * Body Parser Middleware
 * Parse JSON dan URL-encoded bodies
 */
app.use(
  express.json({
    limit: "10mb", // Limit untuk cerita panjang
  }),
);

app.use(
  express.urlencoded({
    extended: true,
    limit: "10mb",
  }),
);

/**
 * Request Logger (Development only)
 * Log setiap request untuk debugging
 */
if (process.env.NODE_ENV === "development") {
  app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${req.method} ${req.url}`);
    next();
  });
}

// =========================================
// ROUTES SETUP
// =========================================

/**
 * API Routes
 * Base path: /api
 */
app.use("/api", routes);

/**
 * Root endpoint
 * Redirect ke health check atau return info
 */
app.get("/", (req, res) => {
  res.json({
    name: "MHCM Chatbot API",
    version: "1.0.0",
    description: "Mental Health Conversational Mirror - Backend Service",
    documentation: "/api",
    health: "/api/health",
  });
});

// =========================================
// ERROR HANDLING
// =========================================

/**
 * 404 Handler
 * Handle routes yang tidak ditemukan
 */
app.use(notFoundHandler);

/**
 * Global Error Handler
 * Handle semua error dari routes dan middleware
 */
app.use(errorHandler);

module.exports = app;
