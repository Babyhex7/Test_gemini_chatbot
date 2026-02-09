/**
 * =========================================
 * Model: QuestionAnswer
 * =========================================
 *
 * Tabel question_answers menyimpan jawaban user untuk pertanyaan validasi.
 * Setiap session punya 5 jawaban (1 set pertanyaan untuk emotion path).
 * Digunakan untuk scoring dan analitik.
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");

const QuestionAnswer = sequelize.define(
  "question_answers",
  {
    // Primary key
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik jawaban",
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

    // Foreign key ke reflection_questions
    question_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
      references: {
        model: "reflection_questions",
        key: "id",
      },
      onDelete: "CASCADE",
      comment: "ID pertanyaan yang dijawab",
    },

    // Emotion key untuk denormalisasi (query cepat)
    emotion_key: {
      type: DataTypes.STRING(100),
      allowNull: false,
      comment: "Emotion key untuk denormalisasi",
    },

    // Index pertanyaan (1-5)
    question_index: {
      type: DataTypes.INTEGER,
      allowNull: false,
      comment: "Urutan pertanyaan dalam set",
    },

    // Teks pertanyaan (snapshot saat dijawab)
    question_text: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Snapshot teks pertanyaan",
    },

    // Jawaban user (A, B, C, atau D)
    user_answer: {
      type: DataTypes.CHAR(1),
      allowNull: false,
      validate: {
        isIn: [["A", "B", "C", "D"]],
      },
      comment: "Jawaban user: A, B, C, atau D",
    },

    // Jawaban yang diharapkan (snapshot)
    expected_answer: {
      type: DataTypes.CHAR(1),
      allowNull: false,
      comment: "Jawaban yang diharapkan",
    },

    // Apakah jawaban benar?
    is_correct: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
      comment: "True jika user_answer = expected_answer",
    },
  },
  {
    tableName: "question_answers",
    timestamps: true,
    underscored: true,

    // Index untuk query performance
    indexes: [
      {
        name: "idx_question_answers_session_id",
        fields: ["session_id"],
      },
      {
        // Satu session hanya bisa jawab satu pertanyaan sekali
        name: "idx_question_answers_unique",
        unique: true,
        fields: ["session_id", "question_id"],
      },
    ],

    // Hook untuk auto-calculate is_correct
    hooks: {
      beforeCreate: (answer) => {
        answer.is_correct = answer.user_answer === answer.expected_answer;
      },
      beforeUpdate: (answer) => {
        if (answer.changed("user_answer")) {
          answer.is_correct = answer.user_answer === answer.expected_answer;
        }
      },
    },
  },
);

/**
 * Static method: Hitung skor untuk session tertentu
 * @param {number} sessionId - ID session
 * @returns {Promise<Object>} - { total, correct, score }
 */
QuestionAnswer.getScoreBySession = async function (sessionId) {
  const answers = await this.findAll({
    where: { session_id: sessionId },
  });

  const total = answers.length;
  const correct = answers.filter((a) => a.is_correct).length;

  return {
    total,
    correct,
    score: total > 0 ? (correct / total) * 100 : 0,
    passed: correct >= 4, // 4-5/5 = confirmed
  };
};

/**
 * Static method: Simpan semua jawaban untuk session
 * @param {number} sessionId - ID session
 * @param {Array} answers - Array of { questionId, userAnswer }
 * @returns {Promise<Object>} - Skor hasil
 */
QuestionAnswer.submitAnswers = async function (sessionId, emotionKey, answers) {
  const ReflectionQuestion = require("./ReflectionQuestion");

  // Ambil pertanyaan untuk validasi
  const questions = await ReflectionQuestion.getByEmotionKey(emotionKey);
  const questionMap = new Map(questions.map((q) => [q.id, q]));

  // Simpan semua jawaban
  const records = answers.map((answer) => {
    const question = questionMap.get(answer.questionId);
    if (!question) {
      throw new Error(`Pertanyaan ${answer.questionId} tidak ditemukan`);
    }

    return {
      session_id: sessionId,
      question_id: answer.questionId,
      emotion_key: emotionKey,
      question_index: question.question_index,
      question_text: question.question_text,
      user_answer: answer.userAnswer.toUpperCase(),
      expected_answer: question.expected_answer,
    };
  });

  await this.bulkCreate(records);

  // Return skor
  return this.getScoreBySession(sessionId);
};

module.exports = QuestionAnswer;
