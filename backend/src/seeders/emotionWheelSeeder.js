/**
 * =========================================
 * Seeder: Emotion Wheel
 * =========================================
 *
 * Seed semua kombinasi emosi dari Feeling Wheel ke database.
 * Total: 7 primary × ~6 secondary × ~3 tertiary
 *
 * Jalankan dengan: npm run db:seed
 * Atau manual: node src/seeders/emotionWheelSeeder.js
 */

require("dotenv").config({
  path: require("path").join(__dirname, "../../.env"),
});
const { sequelize, EmotionWheel } = require("../models");

/**
 * Data Emotion Wheel
 * Format: { primary: { secondary: [tertiary1, tertiary2, ...] } }
 */
const EMOTION_WHEEL_DATA = {
  // 1. HAPPY - Emosi positif
  Happy: {
    Playful: ["Aroused", "Cheeky"],
    Content: ["Free", "Joyful"],
    Interested: ["Curious", "Inquisitive"],
    Proud: ["Successful", "Confident"],
    Accepted: ["Respected", "Valued"],
    Powerful: ["Courageous", "Creative"],
    Peaceful: ["Loving", "Thankful"],
    Trusting: ["Sensitive", "Intimate"],
    Optimistic: ["Hopeful", "Inspired"],
  },

  // 2. SAD - Emosi kesedihan
  Sad: {
    Lonely: ["Isolated", "Abandoned"],
    Vulnerable: ["Victimized", "Fragile"],
    Despair: ["Grief", "Powerless"],
    Guilty: ["Ashamed", "Remorseful"],
    Depressed: ["Inferior", "Empty"],
    Hurt: ["Disappointed", "Embarrassed"],
  },

  // 3. ANGRY - Emosi kemarahan
  Angry: {
    "Let Down": ["Betrayed", "Resentful"],
    Humiliated: ["Disrespected", "Ridiculed"],
    Bitter: ["Indignant", "Violated"],
    Mad: ["Furious", "Jealous"],
    Aggressive: ["Provoked", "Hostile"],
    Frustrated: ["Infuriated", "Annoyed"],
    Distant: ["Withdrawn", "Numb"],
    Critical: ["Skeptical", "Dismissive"],
  },

  // 4. FEARFUL - Emosi ketakutan
  Fearful: {
    Scared: ["Helpless", "Frightened"],
    Anxious: ["Overwhelmed", "Worried"],
    Insecure: ["Inadequate", "Inferior"],
    Weak: ["Worthless", "Insignificant"],
    Rejected: ["Excluded", "Persecuted"],
    Threatened: ["Nervous", "Exposed"],
  },

  // 5. SURPRISED - Emosi terkejut
  Surprised: {
    Startled: ["Shocked", "Dismayed"],
    Confused: ["Disillusioned", "Perplexed"],
    Amazed: ["Astonished", "Awe"],
    Excited: ["Eager", "Energetic"],
  },

  // 6. DISGUSTED - Emosi jijik
  Disgusted: {
    Disapproval: ["Judgmental", "Embarrassed"],
    Disappointed: ["Appalled", "Revolted"],
    Awful: ["Nauseated", "Detestable"],
    Repelled: ["Horrified", "Hesitant"],
  },

  // 7. BAD - Emosi negatif lainnya
  Bad: {
    Bored: ["Indifferent", "Apathetic"],
    Busy: ["Pressured", "Rushed"],
    Stressed: ["Overwhelmed", "Out of Control"],
    Tired: ["Sleepy", "Unfocused"],
  },
};

/**
 * Fungsi untuk seed Emotion Wheel
 */
const seedEmotionWheel = async () => {
  try {
    console.log("🌀 Memulai seeding Emotion Wheel...");

    // Hapus data lama (kalau ada)
    await EmotionWheel.destroy({ where: {} });
    console.log("🗑️  Data lama dihapus");

    // Prepare data untuk bulk insert
    const records = [];

    for (const [primary, secondaries] of Object.entries(EMOTION_WHEEL_DATA)) {
      for (const [secondary, tertiaries] of Object.entries(secondaries)) {
        for (const tertiary of tertiaries) {
          records.push({
            primary,
            secondary,
            tertiary,
            description: `${primary} > ${secondary} > ${tertiary}`,
          });
        }
      }
    }

    // Bulk insert
    await EmotionWheel.bulkCreate(records);

    console.log(`✅ Berhasil insert ${records.length} kombinasi emosi`);
    console.log("\n📊 Ringkasan:");

    // Tampilkan ringkasan per primary
    for (const [primary] of Object.entries(EMOTION_WHEEL_DATA)) {
      const count = await EmotionWheel.count({ where: { primary } });
      console.log(`   - ${primary}: ${count} kombinasi`);
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
    // Test koneksi database
    await sequelize.authenticate();
    console.log("✅ Database terhubung");

    // Sync tabel dulu (kalau belum ada)
    await EmotionWheel.sync({ alter: true });

    // Jalankan seeder
    const success = await seedEmotionWheel();

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

// Jika dijalankan langsung (bukan di-import)
if (require.main === module) {
  runSeeder();
}

module.exports = { seedEmotionWheel, EMOTION_WHEEL_DATA };
