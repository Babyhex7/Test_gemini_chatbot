/**
 * =========================================
 * Model: EmotionWheel
 * =========================================
 *
 * Tabel emotion_wheel menyimpan semua kombinasi emosi dari Feeling Wheel.
 * Struktur: Primary → Secondary → Tertiary
 * Total: 7 primary × ~6 secondary × ~3 tertiary = ~130 kombinasi
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");

const EmotionWheel = sequelize.define(
  "emotion_wheel",
  {
    // Primary key
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik emosi",
    },

    // Primary emotion (Level 1) - 7 emosi utama
    primary: {
      type: DataTypes.STRING(50),
      allowNull: false,
      comment:
        "Primary emotion: Happy, Sad, Angry, Fearful, Surprised, Disgusted, Bad",
    },

    // Secondary emotion (Level 2)
    secondary: {
      type: DataTypes.STRING(50),
      allowNull: false,
      comment: "Secondary emotion: Playful, Content, Lonely, dll",
    },

    // Tertiary emotion (Level 3) - paling spesifik
    tertiary: {
      type: DataTypes.STRING(50),
      allowNull: false,
      comment: "Tertiary emotion: Aroused, Free, Isolated, dll",
    },

    // Deskripsi emosi (opsional, untuk context)
    description: {
      type: DataTypes.TEXT,
      allowNull: true,
      comment: "Deskripsi singkat emosi ini",
    },
  },
  {
    tableName: "emotion_wheel",
    timestamps: true,
    underscored: true,

    // Index untuk query performance
    indexes: [
      {
        name: "idx_emotion_wheel_primary",
        fields: ["primary"],
      },
      {
        name: "idx_emotion_wheel_secondary",
        fields: ["primary", "secondary"],
      },
      {
        // Kombinasi lengkap harus unik
        name: "idx_emotion_wheel_unique",
        unique: true,
        fields: ["primary", "secondary", "tertiary"],
      },
    ],
  },
);

/**
 * Static method: Ambil semua primary emotions
 * @returns {Promise<Array<string>>}
 */
EmotionWheel.getPrimaryEmotions = async function () {
  const results = await this.findAll({
    attributes: [
      [sequelize.fn("DISTINCT", sequelize.col("primary")), "primary"],
    ],
    order: [["primary", "ASC"]],
  });
  return results.map((r) => r.primary);
};

/**
 * Static method: Ambil secondary emotions untuk primary tertentu
 * @param {string} primary - Primary emotion
 * @returns {Promise<Array<string>>}
 */
EmotionWheel.getSecondaryByPrimary = async function (primary) {
  const results = await this.findAll({
    attributes: [
      [sequelize.fn("DISTINCT", sequelize.col("secondary")), "secondary"],
    ],
    where: { primary },
    order: [["secondary", "ASC"]],
  });
  return results.map((r) => r.secondary);
};

/**
 * Static method: Ambil tertiary emotions untuk primary.secondary
 * @param {string} primary
 * @param {string} secondary
 * @returns {Promise<Array<string>>}
 */
EmotionWheel.getTertiaryBySecondary = async function (primary, secondary) {
  const results = await this.findAll({
    attributes: ["tertiary"],
    where: { primary, secondary },
    order: [["tertiary", "ASC"]],
  });
  return results.map((r) => r.tertiary);
};

/**
 * Static method: Validasi apakah kombinasi emosi valid
 * @param {string} primary
 * @param {string} secondary
 * @param {string} tertiary
 * @returns {Promise<boolean>}
 */
EmotionWheel.isValidCombination = async function (
  primary,
  secondary,
  tertiary,
) {
  const count = await this.count({
    where: { primary, secondary, tertiary },
  });
  return count > 0;
};

/**
 * Static method: Cari emosi berdasarkan emotion key
 * @param {string} emotionKey - Format "Primary.Secondary.Tertiary"
 * @returns {Promise<EmotionWheel|null>}
 */
EmotionWheel.findByEmotionKey = async function (emotionKey) {
  const [primary, secondary, tertiary] = emotionKey.split(".");
  return this.findOne({
    where: { primary, secondary, tertiary },
  });
};

/**
 * Instance method: Convert ke emotion key string
 * @returns {string} Format "Primary.Secondary.Tertiary"
 */
EmotionWheel.prototype.toEmotionKey = function () {
  return `${this.primary}.${this.secondary}.${this.tertiary}`;
};

module.exports = EmotionWheel;
