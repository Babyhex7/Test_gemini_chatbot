/**
 * =========================================
 * Model: User
 * =========================================
 *
 * Tabel users menyimpan data pengguna aplikasi.
 * Termasuk autentikasi (email, password) dan profil dasar.
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");
const bcrypt = require("bcryptjs");

const User = sequelize.define(
  "users",
  {
    // Primary key - auto increment
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik user",
    },

    // Nama lengkap user
    name: {
      type: DataTypes.STRING(100),
      allowNull: false,
      validate: {
        notEmpty: { msg: "Nama tidak boleh kosong" },
        len: { args: [2, 100], msg: "Nama harus 2-100 karakter" },
      },
      comment: "Nama lengkap user untuk personalisasi",
    },

    // Email untuk login - harus unik
    email: {
      type: DataTypes.STRING(255),
      allowNull: false,
      unique: {
        name: "users_email_unique",
        msg: "Email sudah terdaftar",
      },
      validate: {
        isEmail: { msg: "Format email tidak valid" },
        notEmpty: { msg: "Email tidak boleh kosong" },
      },
      comment: "Email user untuk login",
    },

    // Password yang sudah di-hash
    password: {
      type: DataTypes.STRING(255),
      allowNull: false,
      validate: {
        notEmpty: { msg: "Password tidak boleh kosong" },
        len: { args: [6, 255], msg: "Password minimal 6 karakter" },
      },
      comment: "Password user (hashed dengan bcrypt)",
    },
  },
  {
    // Nama tabel di database
    tableName: "users",

    // Aktifkan timestamps (created_at, updated_at)
    timestamps: true,

    // Gunakan snake_case untuk nama kolom
    underscored: true,

    // Hooks untuk password hashing
    hooks: {
      // Hash password sebelum create
      beforeCreate: async (user) => {
        if (user.password) {
          const salt = await bcrypt.genSalt(10);
          user.password = await bcrypt.hash(user.password, salt);
        }
      },

      // Hash password sebelum update (jika password berubah)
      beforeUpdate: async (user) => {
        if (user.changed("password")) {
          const salt = await bcrypt.genSalt(10);
          user.password = await bcrypt.hash(user.password, salt);
        }
      },
    },
  },
);

/**
 * Instance method: Bandingkan password input dengan hash
 * @param {string} candidatePassword - Password yang diinput user
 * @returns {Promise<boolean>} - true jika cocok
 */
User.prototype.comparePassword = async function (candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

/**
 * Instance method: Return user tanpa password (untuk response)
 * @returns {Object} - User data tanpa password
 */
User.prototype.toSafeObject = function () {
  const { password, ...safeUser } = this.toJSON();
  return safeUser;
};

module.exports = User;
