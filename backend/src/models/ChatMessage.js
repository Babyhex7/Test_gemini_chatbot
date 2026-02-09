/**
 * =========================================
 * Model: ChatMessage
 * =========================================
 *
 * Tabel chat_messages menyimpan semua pesan dalam session.
 * Termasuk pesan user, bot, dan system messages.
 * Digunakan untuk tracking percakapan dan display chat history.
 */

const { DataTypes } = require("sequelize");
const { sequelize } = require("../config/database");

/**
 * ENUM untuk role pengirim pesan
 * - user: Pesan dari user
 * - bot: Pesan dari chatbot
 * - system: Pesan system (transisi, error, dll)
 */
const MESSAGE_ROLE = {
  USER: "user",
  BOT: "bot",
  SYSTEM: "system",
};

/**
 * ENUM untuk tipe pesan
 * - text: Pesan teks biasa
 * - story: Cerita user (free text panjang)
 * - question: Pertanyaan dari bot (ABCD)
 * - answer: Jawaban user untuk pertanyaan
 * - narrative: Narrative reflektif dari Gemini
 */
const MESSAGE_TYPE = {
  TEXT: "text",
  STORY: "story",
  QUESTION: "question",
  ANSWER: "answer",
  NARRATIVE: "narrative",
};

const ChatMessage = sequelize.define(
  "chat_messages",
  {
    // Primary key
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
      comment: "ID unik pesan",
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

    // Role pengirim pesan
    role: {
      type: DataTypes.ENUM(...Object.values(MESSAGE_ROLE)),
      allowNull: false,
      comment: "Role pengirim: user, bot, system",
    },

    // Tipe pesan
    message_type: {
      type: DataTypes.ENUM(...Object.values(MESSAGE_TYPE)),
      defaultValue: MESSAGE_TYPE.TEXT,
      comment: "Tipe pesan: text, story, question, answer, narrative",
    },

    // Isi pesan
    message: {
      type: DataTypes.TEXT,
      allowNull: false,
      comment: "Isi pesan",
    },

    // Metadata tambahan (JSON)
    // Contoh: { questionId: 1, options: [...] } untuk pertanyaan
    // Contoh: { emotionPath: "Happy.Proud.Confident" } untuk narrative
    metadata: {
      type: DataTypes.JSON,
      allowNull: true,
      comment: "Metadata tambahan dalam format JSON",
    },
  },
  {
    tableName: "chat_messages",
    timestamps: true,
    underscored: true,

    // Index untuk query performance
    indexes: [
      {
        name: "idx_chat_messages_session_id",
        fields: ["session_id"],
      },
      {
        name: "idx_chat_messages_created_at",
        fields: ["created_at"],
      },
    ],
  },
);

/**
 * Static method: Ambil semua pesan dalam session
 * @param {number} sessionId
 * @returns {Promise<Array>}
 */
ChatMessage.getBySession = async function (sessionId) {
  return this.findAll({
    where: { session_id: sessionId },
    order: [["created_at", "ASC"]],
  });
};

/**
 * Static method: Tambah pesan user
 * @param {number} sessionId
 * @param {string} message
 * @param {string} messageType
 * @param {Object} metadata
 * @returns {Promise<ChatMessage>}
 */
ChatMessage.addUserMessage = async function (
  sessionId,
  message,
  messageType = MESSAGE_TYPE.TEXT,
  metadata = null,
) {
  return this.create({
    session_id: sessionId,
    role: MESSAGE_ROLE.USER,
    message_type: messageType,
    message,
    metadata,
  });
};

/**
 * Static method: Tambah pesan bot
 * @param {number} sessionId
 * @param {string} message
 * @param {string} messageType
 * @param {Object} metadata
 * @returns {Promise<ChatMessage>}
 */
ChatMessage.addBotMessage = async function (
  sessionId,
  message,
  messageType = MESSAGE_TYPE.TEXT,
  metadata = null,
) {
  return this.create({
    session_id: sessionId,
    role: MESSAGE_ROLE.BOT,
    message_type: messageType,
    message,
    metadata,
  });
};

/**
 * Static method: Tambah pesan system
 * @param {number} sessionId
 * @param {string} message
 * @param {Object} metadata
 * @returns {Promise<ChatMessage>}
 */
ChatMessage.addSystemMessage = async function (
  sessionId,
  message,
  metadata = null,
) {
  return this.create({
    session_id: sessionId,
    role: MESSAGE_ROLE.SYSTEM,
    message_type: MESSAGE_TYPE.TEXT,
    message,
    metadata,
  });
};

/**
 * Instance method: Format untuk tampilan chat
 * @returns {Object}
 */
ChatMessage.prototype.toChatFormat = function () {
  return {
    id: this.id,
    role: this.role,
    type: this.message_type,
    message: this.message,
    metadata: this.metadata,
    timestamp: this.created_at,
  };
};

// Export model dan constants
module.exports = ChatMessage;
module.exports.MESSAGE_ROLE = MESSAGE_ROLE;
module.exports.MESSAGE_TYPE = MESSAGE_TYPE;
