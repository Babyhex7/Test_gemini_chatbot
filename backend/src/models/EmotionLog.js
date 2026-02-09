/**
 * =========================================
 * Model: EmotionLog
 * =========================================
 *
 * Tabel emotion_logs menyimpan setiap deteksi emosi.
 * Termasuk confidence score, sumber deteksi, dan narrative.
 * Berguna untuk tracking journey emosi user lintas session.
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");

/**
 * ENUM untuk sumber deteksi emosi
 * - ai_detect: Hasil dari Gemini AI
 * - validated: Sudah divalidasi lewat pertanyaan
 */
const DETECTION_SOURCE = {
  AI_DETECT: "ai_detect",
  VALIDATED: "validated",
};

const EmotionLog = sequelize.define(
  "emotion_logs",
  {
    // Primary key
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik emotion log",
    },

    // Foreign key ke sessions
    session_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
      references: {
        model: "sessions",
        key: "id",
      },
      onDelete: "CASCADE",
      comment: "ID session terkait",
    },

    // Foreign key ke users (denormalisasi untuk query cepat)
    user_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
      references: {
        model: "users",
        key: "id",
      },
      onDelete: "CASCADE",
      comment: "ID user pemilik (denormalisasi)",
    },

    // Emosi yang terdeteksi - level primary
    primary_emotion: {
      type: DataTypes.STRING(50),
      allowNull: false,
      comment: "Primary emotion (Happy, Sad, Angry, dll)",
    },

    // Emosi yang terdeteksi - level secondary
    secondary_emotion: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Secondary emotion (Playful, Lonely, dll)",
    },

    // Emosi yang terdeteksi - level tertiary
    tertiary_emotion: {
      type: DataTypes.STRING(50),
      allowNull: true,
      comment: "Tertiary emotion (Aroused, Isolated, dll)",
    },

    // Confidence score dari AI (0.0 - 1.0)
    confidence: {
      type: DataTypes.FLOAT,
      allowNull: true,
      validate: {
        min: 0.0,
        max: 1.0,
      },
      comment: "Confidence score dari AI (0-1)",
    },

    // Sumber deteksi
    source: {
      type: DataTypes.ENUM(...Object.values(DETECTION_SOURCE)),
      defaultValue: DETECTION_SOURCE.AI_DETECT,
      comment: "Sumber deteksi: ai_detect atau validated",
    },

    // Skor validasi per level (berapa soal benar)
    validation_score_primary: {
      type: DataTypes.INTEGER,
      allowNull: true,
      comment: "Skor validasi level primary (deprecated)",
    },

    validation_score_secondary: {
      type: DataTypes.INTEGER,
      allowNull: true,
      comment: "Skor validasi level secondary (deprecated)",
    },

    validation_score_tertiary: {
      type: DataTypes.INTEGER,
      allowNull: true,
      comment: "Skor validasi dari 5 soal ABCD",
    },

    // Narrative yang digenerate Gemini
    narrative: {
      type: DataTypes.TEXT,
      allowNull: true,
      comment: "Narrative reflektif dari Gemini",
    },

    // Journey note dari AI (pattern awareness)
    journey_note: {
      type: DataTypes.STRING(255),
      allowNull: true,
      comment: "Catatan journey dari AI (trending, recurring)",
    },

    // Waktu deteksi
    detected_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
      comment: "Waktu deteksi emosi",
    },
  },
  {
    tableName: "emotion_logs",
    timestamps: true,
    underscored: true,

    // Index untuk query performance
    indexes: [
      {
        name: "idx_emotion_logs_user_id",
        fields: ["user_id"],
      },
      {
        name: "idx_emotion_logs_session_id",
        fields: ["session_id"],
      },
      {
        name: "idx_emotion_logs_detected_at",
        fields: ["detected_at"],
      },
    ],
  },
);

/**
 * Instance method: Dapatkan emotion path sebagai string
 * @returns {string} Format "Primary.Secondary.Tertiary"
 */
EmotionLog.prototype.getEmotionPath = function () {
  const parts = [this.primary_emotion];
  if (this.secondary_emotion) parts.push(this.secondary_emotion);
  if (this.tertiary_emotion) parts.push(this.tertiary_emotion);
  return parts.join(".");
};

/**
 * Instance method: Format untuk history display
 * @returns {Object} Ringkasan untuk tampilan/inject
 */
EmotionLog.prototype.toHistorySummary = function () {
  return {
    date: this.detected_at,
    emotion: this.getEmotionPath(),
    confidence: this.confidence,
    hasNarrative: !!this.narrative,
  };
};

// Export model dan constants
module.exports = EmotionLog;
module.exports.DETECTION_SOURCE = DETECTION_SOURCE;
