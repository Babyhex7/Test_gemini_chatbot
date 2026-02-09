/**
 * =========================================
 * MHCM Chatbot - Server Entry Point
 * =========================================
 *
 * File ini adalah entry point aplikasi.
 * Menghubungkan ke database lalu start Express server.
 */

const app = require("./app");
const { testConnection, syncDatabase } = require("./models");

// Port server
const PORT = process.env.PORT || 5000;

/**
 * Fungsi startup server
 * 1. Test koneksi database
 * 2. Sync schema (development only)
 * 3. Start Express server
 */
const startServer = async () => {
  try {
    console.log("🚀 Memulai MHCM Chatbot Backend...");
    console.log(`📍 Environment: ${process.env.NODE_ENV || "development"}`);

    // Step 1: Test koneksi database
    console.log("\n📦 Menghubungkan ke database...");
    const dbConnected = await testConnection();

    if (!dbConnected) {
      console.error("❌ Gagal terhubung ke database. Server tidak dimulai.");
      process.exit(1);
    }

    // Step 2: Sync database schema (development only)
    if (process.env.NODE_ENV === "development") {
      console.log("\n🔄 Sync database schema...");
      await syncDatabase({ alter: true });
    }

    // Step 3: Start Express server
    app.listen(PORT, () => {
      console.log("\n=========================================");
      console.log(`✅ Server berjalan di http://localhost:${PORT}`);
      console.log(`📚 API Docs: http://localhost:${PORT}/api`);
      console.log(`💓 Health Check: http://localhost:${PORT}/api/health`);
      console.log("=========================================\n");
    });
  } catch (error) {
    console.error("❌ Gagal memulai server:", error.message);
    process.exit(1);
  }
};

// =========================================
// GRACEFUL SHUTDOWN
// =========================================

/**
 * Handle graceful shutdown
 * Tutup koneksi database dengan benar saat server di-stop
 */
process.on("SIGTERM", async () => {
  console.log("\n⚠️ SIGTERM received. Shutting down gracefully...");

  // Tutup koneksi database
  const { sequelize } = require("./models");
  await sequelize.close();

  console.log("👋 Server shut down.");
  process.exit(0);
});

process.on("SIGINT", async () => {
  console.log("\n⚠️ SIGINT received. Shutting down gracefully...");

  const { sequelize } = require("./models");
  await sequelize.close();

  console.log("👋 Server shut down.");
  process.exit(0);
});

// =========================================
// START SERVER
// =========================================

startServer();
