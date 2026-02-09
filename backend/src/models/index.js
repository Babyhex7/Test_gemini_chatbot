/**
 * =========================================
 * Models Index - Central Export
 * =========================================
 *
 * File ini:
 * 1. Import semua model
 * 2. Setup associations (relasi antar tabel)
 * 3. Export semua model dan sequelize instance
 *
 * Import file ini untuk akses ke semua model.
 */

const {
  sequelize,
  testConnection,
  syncDatabase,
} = require("../config/database");

// Import semua model
const User = require("./User");
const Session = require("./Session");
const EmotionLog = require("./EmotionLog");
const ReflectionQuestion = require("./ReflectionQuestion");
const QuestionAnswer = require("./QuestionAnswer");
const EmotionWheel = require("./EmotionWheel");
const ChatMessage = require("./ChatMessage");

// =========================================
// ASSOCIATIONS (Relasi Antar Tabel)
// =========================================

/**
 * User ↔ Session
 * Satu user bisa punya banyak session (1:N)
 */
User.hasMany(Session, {
  foreignKey: "user_id",
  as: "sessions",
});

Session.belongsTo(User, {
  foreignKey: "user_id",
  as: "user",
});

/**
 * User ↔ EmotionLog
 * Satu user bisa punya banyak emotion logs (1:N)
 * Denormalisasi untuk query cepat "emotion journey user"
 */
User.hasMany(EmotionLog, {
  foreignKey: "user_id",
  as: "emotionLogs",
});

EmotionLog.belongsTo(User, {
  foreignKey: "user_id",
  as: "user",
});

/**
 * Session ↔ EmotionLog
 * Satu session bisa punya satu atau lebih emotion logs (1:N)
 * Biasanya 1 session = 1 emotion log (setelah validasi)
 */
Session.hasMany(EmotionLog, {
  foreignKey: "session_id",
  as: "emotionLogs",
});

EmotionLog.belongsTo(Session, {
  foreignKey: "session_id",
  as: "session",
});

/**
 * Session ↔ QuestionAnswer
 * Satu session punya 5 jawaban pertanyaan (1:N)
 */
Session.hasMany(QuestionAnswer, {
  foreignKey: "session_id",
  as: "answers",
});

QuestionAnswer.belongsTo(Session, {
  foreignKey: "session_id",
  as: "session",
});

/**
 * ReflectionQuestion ↔ QuestionAnswer
 * Satu pertanyaan bisa dijawab di banyak session (1:N)
 */
ReflectionQuestion.hasMany(QuestionAnswer, {
  foreignKey: "question_id",
  as: "answers",
});

QuestionAnswer.belongsTo(ReflectionQuestion, {
  foreignKey: "question_id",
  as: "question",
});

/**
 * Session ↔ ChatMessage
 * Satu session punya banyak chat messages (1:N)
 */
Session.hasMany(ChatMessage, {
  foreignKey: "session_id",
  as: "messages",
});

ChatMessage.belongsTo(Session, {
  foreignKey: "session_id",
  as: "session",
});

// =========================================
// EXPORT
// =========================================

module.exports = {
  // Sequelize instance & helpers
  sequelize,
  testConnection,
  syncDatabase,

  // Models
  User,
  Session,
  EmotionLog,
  ReflectionQuestion,
  QuestionAnswer,
  EmotionWheel,
  ChatMessage,

  // Constants re-export untuk convenience
  SESSION_STATUS: Session.SESSION_STATUS,
  FLOW_STATES: Session.FLOW_STATES,
  DETECTION_SOURCE: EmotionLog.DETECTION_SOURCE,
  MESSAGE_ROLE: ChatMessage.MESSAGE_ROLE,
  MESSAGE_TYPE: ChatMessage.MESSAGE_TYPE,
};
