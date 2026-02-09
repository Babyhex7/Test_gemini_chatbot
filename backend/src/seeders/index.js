/**
 * =========================================
 * Seeder Index - Run All Seeders
 * =========================================
 *
 * Jalankan semua seeder dalam urutan yang benar.
 * Gunakan: node src/seeders/index.js
 */

require("dotenv").config({
  path: require("path").join(__dirname, "../../.env"),
});
const { sequelize, syncDatabase } = require("../models");
const { seedEmotionWheel } = require("./emotionWheelSeeder");
const { seedReflectionQuestions } = require("./reflectionQuestionsSeeder");

/**
 * Jalankan semua seeder
 */
const runAllSeeders = async () => {
  try {
    console.log("=========================================");
    console.log("🌱 MHCM Chatbot - Database Seeder");
    console.log("=========================================\n");

    // Test koneksi
    await sequelize.authenticate();
    console.log("✅ Database terhubung\n");

    // Sync semua tabel
    console.log("🔄 Sync database schema...");
    await syncDatabase({ alter: true });
    console.log("");

    // 1. Seed Emotion Wheel
    console.log("=========================================");
    await seedEmotionWheel();
    console.log("");

    // 2. Seed Reflection Questions
    console.log("=========================================");
    await seedReflectionQuestions();
    console.log("");

    console.log("=========================================");
    console.log("🎉 Semua seeding selesai!");
    console.log("=========================================");
  } catch (error) {
    console.error("❌ Error:", error.message);
    console.error(error.stack);
  } finally {
    await sequelize.close();
    process.exit(0);
  }
};

runAllSeeders();
