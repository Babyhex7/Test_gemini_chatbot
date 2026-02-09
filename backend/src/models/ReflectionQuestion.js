/**
 * =========================================
 * Model: ReflectionQuestion
 * =========================================
 *
 * Tabel reflection_questions menyimpan pertanyaan validasi ABCD.
 * Setiap kombinasi emosi (emotion_key) punya 5 pertanyaan unik.
 * Format emotion_key: "Happy.Proud.Confident"
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");

const ReflectionQuestion = sequelize.define(
  "reflection_questions",
  {
    // Primary key
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik pertanyaan",
    },

    // Emotion key - kombinasi emosi lengkap
    // Format: "Primary.Secondary.Tertiary" (e.g., "Happy.Proud.Confident")
    emotion_key: {
      type: DataTypes.STRING(100),
      allowNull: false,
      comment: "Kombinasi emosi: Primary.Secondary.Tertiary",
    },

    // Index pertanyaan dalam set (1-5)
    question_index: {
      type: DataTypes.INTEGER,
      allowNull: false,
      validate: {
        min: 1,
        max: 10,
      },
      comment: "Urutan pertanyaan dalam set (1-5)",
    },

    // Teks pertanyaan
    question_text: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Teks pertanyaan untuk user",
    },

    // Opsi jawaban A
    option_a: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Opsi jawaban A",
    },

    // Opsi jawaban B
    option_b: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Opsi jawaban B",
    },

    // Opsi jawaban C - jawaban yang diharapkan
    option_c: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Opsi jawaban C (expected answer)",
    },

    // Opsi jawaban D
    option_d: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Opsi jawaban D",
    },

    // Jawaban yang diharapkan (selalu C dalam desain ini)
    expected_answer: {
      type: DataTypes.CHAR(1),
      allowNull: false,
      defaultValue: "C",
      validate: {
        isIn: [["A", "B", "C", "D"]],
      },
      comment: "Jawaban yang diharapkan (default: C)",
    },
  },
  {
    tableName: "reflection_questions",
    timestamps: true,
    underscored: true,

    // Index untuk query performance
    indexes: [
      {
        name: "idx_reflection_questions_emotion_key",
        fields: ["emotion_key"],
      },
      {
        // Kombinasi emotion_key + question_index harus unik
        name: "idx_reflection_questions_unique",
        unique: true,
        fields: ["emotion_key", "question_index"],
      },
    ],
  },
);

/**
 * Static method: Ambil semua pertanyaan untuk emotion key tertentu
 * @param {string} emotionKey - Format "Primary.Secondary.Tertiary"
 * @returns {Promise<Array>} - Array pertanyaan berurutan
 */
ReflectionQuestion.getByEmotionKey = async function (emotionKey) {
  return this.findAll({
    where: { emotion_key: emotionKey },
    order: [["question_index", "ASC"]],
  });
};

/**
 * Instance method: Format untuk ditampilkan ke user
 * @returns {Object} - Pertanyaan dengan opsi dalam format array
 */
ReflectionQuestion.prototype.toQuestionFormat = function () {
  return {
    id: this.id,
    questionIndex: this.question_index,
    questionText: this.question_text,
    options: [
      { key: "A", text: this.option_a },
      { key: "B", text: this.option_b },
      { key: "C", text: this.option_c },
      { key: "D", text: this.option_d },
    ],
  };
};

module.exports = ReflectionQuestion;
