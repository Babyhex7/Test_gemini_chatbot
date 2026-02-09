/**
 * =========================================
 * Seeder: Reflection Questions
 * =========================================
 *
 * Seed pertanyaan validasi ABCD untuk beberapa emotion path contoh.
 * Pertanyaan lengkap akan ditambahkan secara bertahap.
 *
 * Format emotion_key: "Primary.Secondary.Tertiary"
 * Setiap emotion path punya 5 pertanyaan unik
 */

require("dotenv").config({
  path: require("path").join(__dirname, "../../.env"),
});
const { sequelize, ReflectionQuestion } = require("../models");

/**
 * Sample Reflection Questions
 *
 * NOTE: Ini hanya contoh untuk beberapa emotion path.
 * Pertanyaan lengkap untuk semua ~130 path akan ditambahkan nanti.
 *
 * Format: { emotion_key: [{ question_text, option_a, option_b, option_c (expected), option_d }] }
 */
const SAMPLE_QUESTIONS = {
  // =========================================
  // HAPPY > PROUD > CONFIDENT
  // =========================================
  "Happy.Proud.Confident": [
    {
      question_index: 1,
      question_text:
        "Akhir-akhir ini, apakah kamu merasa yakin dengan kemampuanmu?",
      option_a: "Tidak, aku merasa ragu dengan diriku",
      option_b: "Kadang-kadang saja",
      option_c: "Ya, aku merasa percaya diri dengan apa yang bisa aku lakukan",
      option_d: "Aku tidak terlalu memikirkannya",
      expected_answer: "C",
    },
    {
      question_index: 2,
      question_text:
        "Ketika menghadapi tantangan baru, apa yang biasanya kamu rasakan?",
      option_a: "Takut gagal",
      option_b: "Biasa saja, tidak ada perasaan khusus",
      option_c: "Antusias dan yakin bisa mengatasinya",
      option_d: "Cenderung menghindarinya",
      expected_answer: "C",
    },
    {
      question_index: 3,
      question_text: "Bagaimana kamu melihat pencapaianmu selama ini?",
      option_a: "Aku merasa belum mencapai apa-apa",
      option_b: "Lumayan, tapi masih banyak kekurangan",
      option_c: "Aku bangga dengan perjalanan dan pencapaianku",
      option_d: "Aku jarang merefleksikan pencapaianku",
      expected_answer: "C",
    },
    {
      question_index: 4,
      question_text:
        "Saat orang lain meminta pendapatmu, apa yang kamu rasakan?",
      option_a: "Gugup karena takut salah",
      option_b: "Netral, tergantung situasi",
      option_c: "Nyaman karena aku percaya pada penilaianku",
      option_d: "Tidak nyaman memberikan pendapat",
      expected_answer: "C",
    },
    {
      question_index: 5,
      question_text:
        "Bagaimana kamu menggambarkan hubunganmu dengan dirimu sendiri?",
      option_a: "Seringkali kritis dan negatif",
      option_b: "Kadang baik kadang buruk",
      option_c: "Positif, aku menerima dan menghargai diriku",
      option_d: "Aku jarang memikirkan hal ini",
      expected_answer: "C",
    },
  ],

  // =========================================
  // SAD > LONELY > ISOLATED
  // =========================================
  "Sad.Lonely.Isolated": [
    {
      question_index: 1,
      question_text:
        "Akhir-akhir ini, apakah kamu merasa terpisah dari orang-orang di sekitarmu?",
      option_a: "Tidak, aku merasa dekat dengan mereka",
      option_b: "Kadang-kadang saja",
      option_c: "Ya, seperti ada jarak yang sulit dijelaskan",
      option_d: "Aku tidak yakin",
      expected_answer: "C",
    },
    {
      question_index: 2,
      question_text: "Ketika ada acara sosial, apa yang biasanya kamu rasakan?",
      option_a: "Antusias untuk datang dan berinteraksi",
      option_b: "Biasa saja",
      option_c: "Lebih memilih menyendiri atau merasa tidak terkoneksi",
      option_d: "Tergantung acaranya",
      expected_answer: "C",
    },
    {
      question_index: 3,
      question_text:
        "Apakah kamu merasa sulit untuk berbagi perasaan dengan orang lain?",
      option_a: "Tidak, aku mudah terbuka",
      option_b: "Dengan beberapa orang tertentu saja",
      option_c: "Ya, aku merasa tidak ada yang benar-benar mengerti",
      option_d: "Aku tidak suka berbagi perasaan",
      expected_answer: "C",
    },
    {
      question_index: 4,
      question_text:
        "Bagaimana kamu menggambarkan koneksimu dengan lingkungan sosial?",
      option_a: "Sangat terhubung dan aktif",
      option_b: "Cukup terhubung",
      option_c: "Merasa berada di luar, seperti penonton",
      option_d: "Aku tidak membutuhkan koneksi sosial",
      expected_answer: "C",
    },
    {
      question_index: 5,
      question_text: "Saat sendiri, apa yang paling sering kamu rasakan?",
      option_a: "Nyaman dan tenang",
      option_b: "Biasa saja",
      option_c: "Hampa atau kesepian yang dalam",
      option_d: "Produktif karena bisa fokus",
      expected_answer: "C",
    },
  ],

  // =========================================
  // FEARFUL > ANXIOUS > OVERWHELMED
  // =========================================
  "Fearful.Anxious.Overwhelmed": [
    {
      question_index: 1,
      question_text:
        "Apakah kamu sering merasa kewalahan dengan banyaknya hal yang harus diurus?",
      option_a: "Tidak, aku bisa mengelolanya dengan baik",
      option_b: "Sesekali saja",
      option_c: "Ya, rasanya terlalu banyak dan sulit ditangani",
      option_d: "Aku cenderung mengabaikan masalah",
      expected_answer: "C",
    },
    {
      question_index: 2,
      question_text: "Bagaimana tidurmu akhir-akhir ini?",
      option_a: "Nyenyak dan cukup",
      option_b: "Lumayan baik",
      option_c: "Terganggu karena pikiran yang tidak berhenti",
      option_d: "Tidak ada perubahan signifikan",
      expected_answer: "C",
    },
    {
      question_index: 3,
      question_text:
        "Saat memikirkan semua tanggung jawabmu, apa yang kamu rasakan?",
      option_a: "Termotivasi untuk menyelesaikannya",
      option_b: "Biasa saja",
      option_c: "Cemas atau panik karena terlalu banyak",
      option_d: "Aku mencoba tidak memikirkannya",
      expected_answer: "C",
    },
    {
      question_index: 4,
      question_text:
        "Apakah kamu sering merasa sulit untuk rileks atau menenangkan pikiran?",
      option_a: "Tidak, aku bisa rileks dengan mudah",
      option_b: "Kadang-kadang",
      option_c: "Ya, pikiran selalu racing dan sulit berhenti",
      option_d: "Aku tidak punya waktu untuk rileks",
      expected_answer: "C",
    },
    {
      question_index: 5,
      question_text: "Bagaimana tubuhmu merespons stres akhir-akhir ini?",
      option_a: "Normal, tidak ada keluhan fisik",
      option_b: "Sedikit lelah tapi masih oke",
      option_c: "Tegang, sakit kepala, atau gejala fisik lainnya",
      option_d: "Aku tidak memperhatikan tubuhku",
      expected_answer: "C",
    },
  ],

  // =========================================
  // ANGRY > FRUSTRATED > ANNOYED
  // =========================================
  "Angry.Frustrated.Annoyed": [
    {
      question_index: 1,
      question_text:
        "Apakah akhir-akhir ini hal-hal kecil lebih mudah membuatmu kesal?",
      option_a: "Tidak, aku masih sabar",
      option_b: "Kadang-kadang",
      option_c: "Ya, aku lebih mudah terpicu oleh hal-hal sepele",
      option_d: "Aku tidak memperhatikan",
      expected_answer: "C",
    },
    {
      question_index: 2,
      question_text:
        "Bagaimana reaksimu saat sesuatu tidak berjalan sesuai rencana?",
      option_a: "Aku menerima dan mencari solusi",
      option_b: "Sedikit kecewa tapi move on",
      option_c: "Frustrasi dan kesal berkepanjangan",
      option_d: "Aku tidak punya ekspektasi",
      expected_answer: "C",
    },
    {
      question_index: 3,
      question_text:
        "Apakah kamu merasa kesabaranmu lebih tipis dari biasanya?",
      option_a: "Tidak, kesabaranku masih normal",
      option_b: "Sedikit lebih sensitif",
      option_c: "Ya, aku lebih cepat marah atau kesal",
      option_d: "Aku selalu tidak sabar",
      expected_answer: "C",
    },
    {
      question_index: 4,
      question_text:
        "Saat ada orang yang melakukan kesalahan kecil, apa responmu?",
      option_a: "Memaklumi dan membantu",
      option_b: "Netral, tidak terlalu peduli",
      option_c: "Kesal meskipun tahu itu tidak seharusnya",
      option_d: "Tergantung siapa orangnya",
      expected_answer: "C",
    },
    {
      question_index: 5,
      question_text:
        "Bagaimana kamu menggambarkan tingkat iritasimu akhir-akhir ini?",
      option_a: "Rendah, aku cukup tenang",
      option_b: "Normal, seperti biasa",
      option_c: "Tinggi, banyak hal yang membuatku jengkel",
      option_d: "Aku tidak memperhatikan emosiku",
      expected_answer: "C",
    },
  ],

  // =========================================
  // SURPRISED > AMAZED > ASTONISHED
  // =========================================
  "Surprised.Amazed.Astonished": [
    {
      question_index: 1,
      question_text:
        "Apakah ada sesuatu yang baru-baru ini membuatmu sangat takjub?",
      option_a: "Tidak ada yang spesial",
      option_b: "Mungkin sedikit",
      option_c: "Ya, ada sesuatu yang benar-benar mengagumkan",
      option_d: "Aku jarang merasa takjub",
      expected_answer: "C",
    },
    {
      question_index: 2,
      question_text:
        "Bagaimana kamu menggambarkan perasaanmu terhadap sesuatu yang baru kamu temui?",
      option_a: "Biasa saja",
      option_b: "Sedikit tertarik",
      option_c: "Sangat terkesan dan kagum",
      option_d: "Skeptis",
      expected_answer: "C",
    },
    {
      question_index: 3,
      question_text:
        "Apakah kamu merasa dunia ini masih menyimpan banyak hal menakjubkan?",
      option_a: "Tidak, semuanya sudah predictable",
      option_b: "Mungkin sedikit",
      option_c: "Ya, ada begitu banyak keajaiban yang belum kutemukan",
      option_d: "Aku tidak memikirkan hal itu",
      expected_answer: "C",
    },
    {
      question_index: 4,
      question_text:
        "Saat melihat sesuatu yang luar biasa, apa reaksi pertamamu?",
      option_a: "Curiga atau mencari kelemahannya",
      option_b: "Netral",
      option_c: "Terpesona dan ingin tahu lebih banyak",
      option_d: "Tidak ada reaksi khusus",
      expected_answer: "C",
    },
    {
      question_index: 5,
      question_text:
        "Bagaimana kamu memproses pengalaman yang benar-benar mengejutkan (positif)?",
      option_a: "Cepat move on",
      option_b: "Memikirkannya sebentar lalu lupa",
      option_c: "Meresapi dan menyimpannya sebagai momen berharga",
      option_d: "Aku jarang punya pengalaman seperti itu",
      expected_answer: "C",
    },
  ],
};

/**
 * Fungsi untuk seed Reflection Questions
 */
const seedReflectionQuestions = async () => {
  try {
    console.log("❓ Memulai seeding Reflection Questions...");

    // Hapus data lama (kalau ada)
    await ReflectionQuestion.destroy({ where: {} });
    console.log("🗑️  Data lama dihapus");

    // Prepare data untuk bulk insert
    const records = [];

    for (const [emotionKey, questions] of Object.entries(SAMPLE_QUESTIONS)) {
      for (const question of questions) {
        records.push({
          emotion_key: emotionKey,
          ...question,
        });
      }
    }

    // Bulk insert
    await ReflectionQuestion.bulkCreate(records);

    console.log(`✅ Berhasil insert ${records.length} pertanyaan`);
    console.log("\n📊 Ringkasan:");

    for (const emotionKey of Object.keys(SAMPLE_QUESTIONS)) {
      const count = await ReflectionQuestion.count({
        where: { emotion_key: emotionKey },
      });
      console.log(`   - ${emotionKey}: ${count} pertanyaan`);
    }

    return true;
  } catch (error) {
    console.error("❌ Gagal seeding:", error.message);
    return false;
  }
};

/**
 * Jalankan seeder jika file ini dieksekusi langsung
 */
const runSeeder = async () => {
  try {
    await sequelize.authenticate();
    console.log("✅ Database terhubung");

    await ReflectionQuestion.sync({ alter: true });
    const success = await seedReflectionQuestions();

    if (success) {
      console.log("\n🎉 Seeding selesai!");
    }
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await sequelize.close();
    process.exit(0);
  }
};

if (require.main === module) {
  runSeeder();
}

module.exports = { seedReflectionQuestions, SAMPLE_QUESTIONS };
