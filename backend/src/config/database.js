/**
 * =========================================
 * MHCM Chatbot - Konfigurasi Database
 * =========================================
 *
 * File ini mengatur koneksi ke MySQL menggunakan Sequelize ORM.
 * Konfigurasi diambil dari environment variables (.env)
 */

require("dotenv").config();
const { Sequelize } = require("sequelize");

// Buat instance Sequelize dengan konfigurasi MySQL
const sequelize = new Sequelize(
  process.env.DB_NAME || "mhcm_chatbot", // Nama database
  process.env.DB_USER || "root", // Username MySQL
  process.env.DB_PASSWORD || "", // Password MySQL
  {
    host: process.env.DB_HOST || "localhost", // Host database
    port: process.env.DB_PORT || 3306, // Port MySQL
    dialect: "mysql", // Tipe database: MySQL

    // Konfigurasi logging - hanya tampilkan query di development
    logging: process.env.NODE_ENV === "development" ? console.log : false,

    // Konfigurasi connection pool untuk performa
    pool: {
      max: 10, // Maksimal 10 koneksi dalam pool
      min: 0, // Minimal 0 koneksi (buat baru kalau perlu)
      acquire: 30000, // Timeout 30 detik untuk acquire koneksi
      idle: 10000, // Tutup koneksi idle setelah 10 detik
    },

    // Timezone untuk konsistensi waktu dengan Indonesia
    timezone: "+07:00",

    // Konfigurasi model default
    define: {
      timestamps: true, // Otomatis tambahkan createdAt & updatedAt
      underscored: true, // Gunakan snake_case untuk nama kolom (best practice SQL)
      freezeTableName: true, // Jangan ubah nama tabel jadi plural
    },
  },
);

/**
 * Fungsi untuk test koneksi database
 * Dipanggil saat startup untuk memastikan DB tersambung
 */
const testConnection = async () => {
  try {
    await sequelize.authenticate();
    console.log("✅ Database terhubung dengan sukses!");
    return true;
  } catch (error) {
    console.error("❌ Gagal terhubung ke database:", error.message);
    return false;
  }
};

/**
 * Fungsi untuk sync semua model ke database
 * Gunakan alter: true untuk update schema tanpa drop data
 * PERINGATAN: Jangan gunakan force: true di production!
 */
const syncDatabase = async (options = {}) => {
  try {
    // Default: alter mode untuk development
    const syncOptions = {
      alter: process.env.NODE_ENV === "development",
      ...options,
    };

    await sequelize.sync(syncOptions);
    console.log("✅ Database schema berhasil di-sync!");
    return true;
  } catch (error) {
    console.error("❌ Gagal sync database:", error.message);
    return false;
  }
};

module.exports = {
  sequelize,
  testConnection,
  syncDatabase,
};
