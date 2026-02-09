/**
 * =========================================
 * Model: Session
 * =========================================
 *
 * Tabel sessions menyimpan setiap sesi percakapan user.
 * Termasuk cerita user, emosi terdeteksi, dan flow state.
 * Satu user bisa punya banyak session (1:N).
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");

/**
 * ENUM untuk status session
 * - active: Session sedang berjalan
 * - completed: Session selesai dengan narrative
 * - abandoned: Session ditinggalkan user
 */
const SESSION_STATUS = {
  ACTIVE: "active",
  COMPLETED: "completed",
  ABANDONED: "abandoned",
};

/**
 * ENUM untuk flow state (state machine)
 * Menentukan posisi user dalam alur percakapan
 */
const FLOW_STATES = {
  SAFE_FRAMING: "SAFE_FRAMING", // Pembuka safe space
  STORYTELLING: "STORYTELLING", // User sedang bercerita
  STORY_TOLD: "STORY_TOLD", // Cerita diterima, AI detecting
  VALIDATE_EMOTION: "VALIDATE_EMOTION", // User menjawab pertanyaan
  NARRATIVE: "NARRATIVE", // Narrative ditampilkan
  COMPLETED: "COMPLETED", // Session selesai
};

const Session = sequelize.define(
  "sessions",
  {
    // Primary key
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik session",
    },

    // Foreign key ke tabel users
    user_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
      references: {
        model: "users",
        key: "id",
      },
      onDelete: "CASCADE",
      comment: "ID user pemilik session",
    },

    // State machine - posisi dalam flow
    flow_state: {
      type: DataTypes.ENUM(...Object.values(FLOW_STATES)),
      defaultValue: FLOW_STATES.SAFE_FRAMING,
      allowNull: false,
      comment: "Posisi user dalam flow percakapan",
    },

    // Cerita lengkap user (free text)
    story_text: {
      type: DataTypes.TEXT,
      allowNull: true,
      comment: "Cerita lengkap dari user untuk konteks",
    },

    // Ringkasan cerita untuk inject ke prompt (max 200 karakter)
    story_summary: {
      type: DataTypes.STRING(200),
      allowNull: true,
      comment: "Ringkasan cerita untuk cross-session history",
    },

    // Emosi yang terdeteksi AI (sebelum validasi)
    detected_primary: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Primary emotion dari AI detection",
    },

    detected_secondary: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Secondary emotion dari AI detection",
    },

    detected_tertiary: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Tertiary emotion dari AI detection",
    },

    // Emosi final setelah validasi user
    final_primary: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Primary emotion setelah validasi",
    },

    final_secondary: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Secondary emotion setelah validasi",
    },

    final_tertiary: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Tertiary emotion setelah validasi",
    },

    // Status session
    status: {
      type: DataTypes.ENUM(...Object.values(SESSION_STATUS)),
      defaultValue: SESSION_STATUS.ACTIVE,
      allowNull: false,
      comment: "Status session: active, completed, abandoned",
    },

    // Kapan session dimulai
    started_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
      comment: "Waktu mulai session",
    },

    // Kapan session berakhir (nullable sampai selesai)
    ended_at: {
      type: DataTypes.DATE,
      allowNull: true,
      comment: "Waktu selesai session",
    },
  },
  {
    tableName: "sessions",
    timestamps: true,
    underscored: true,

    // Index untuk query performance
    indexes: [
      {
        name: "idx_sessions_user_id",
        fields: ["user_id"],
      },
      {
        name: "idx_sessions_status",
        fields: ["status"],
      },
      {
        name: "idx_sessions_created_at",
        fields: ["created_at"],
      },
    ],
  },
);

/**
 * Instance method: Dapatkan emotion key untuk query questions
 * Format: "Primary.Secondary.Tertiary"
 */
Session.prototype.getEmotionKey = function () {
  const primary = this.final_primary || this.detected_primary;
  const secondary = this.final_secondary || this.detected_secondary;
  const tertiary = this.final_tertiary || this.detected_tertiary;

  if (primary && secondary && tertiary) {
    return `${primary}.${secondary}.${tertiary}`;
  }
  return null;
};

/**
 * Instance method: Tandai session sebagai selesai
 */
Session.prototype.markCompleted = async function () {
  this.status = SESSION_STATUS.COMPLETED;
  this.flow_state = FLOW_STATES.COMPLETED;
  this.ended_at = new Date();
  await this.save();
};

// Export model dan constants
module.exports = Session;
module.exports.SESSION_STATUS = SESSION_STATUS;
module.exports.FLOW_STATES = FLOW_STATES;
