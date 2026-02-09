# MHCM Chatbot — Architecture Brief Document

> Mental Health Conversational Mirror — Emotion Checker via Storytelling
> **Versi: 3.0 (Revisi)** | Tanggal: 8 Februari 2026

---

## 1. Ringkasan Produk

Chatbot refleksi emosi berbasis storytelling. User bercerita tentang kejadian/perasaannya,
lalu sistem mendeteksi emosi, memvalidasi lewat **pertanyaan refleksi (pilihan ganda ABCD)**
yang spesifik untuk **kombinasi emosi lengkap**, dan menghasilkan narasi reflektif yang empatik — **bukan diagnosis klinis**.

**Prinsip Utama:**

- Refleksi, bukan diagnosis
- Bahasa manusiawi, bukan label klinis
- User bercerita → sistem merespons dengan empati
- Pertanyaan follow-up spesifik untuk **setiap path emosi** (e.g., Happy.Proud.Confident vs Happy.Accepted.Respected)
- **Chat memory**: sistem ingat konteks percakapan dalam session (seperti ChatGPT)
- Hanya 1 jenis pertanyaan: **Reflection Questions (ABCD)** per emotion path

---

## 2. Tech Stack

```
┌──────────────┬──────────────────────────────────────────────────┐
│ Layer        │ Teknologi                                        │
├──────────────┼──────────────────────────────────────────────────┤
│ Frontend     │ React.js + TypeScript + Tailwind CSS             │
│ Backend      │ Node.js + Express.js                             │
│ AI Service   │ Python + FastAPI + Google Gemini API (free tier) │
│ Database     │ MySQL + Sequelize ORM                            │
│ Realtime     │ Socket.IO (optional, untuk typing indicator)     │
│ Deployment   │ Docker Compose                                   │
└──────────────┴──────────────────────────────────────────────────┘
```

**Kenapa 3 service terpisah?**

| Service                    | Tanggung Jawab                                                         | Alasan Pisah                                 |
| -------------------------- | ---------------------------------------------------------------------- | -------------------------------------------- |
| **Frontend (React)**       | UI chat, tampilkan pilihan ganda, tampilkan narasi                     | SPA ringan, bisa di-deploy ke Vercel/Netlify |
| **Backend (Node/Express)** | Auth, session, CRUD, flow engine, simpan data, load pertanyaan dari DB | Sequelize + MySQL, state machine logic       |
| **AI Service (FastAPI)**   | Gemini calls: detect emotion dari cerita + generate narrative          | Python async cocok untuk LLM calls           |

---

## 3. Apa yang Dikerjakan Gemini vs Apa yang Statis

```
┌─────────────────────────────────────────────────────────────────────┐
│                🤖 GEMINI (via AI Service FastAPI)                    │
│                                                                     │
│  Hanya dipanggil untuk 2 hal:                                       │
│                                                                     │
│  1. DETECT EMOTION dari cerita user                                 │
│     Input: teks cerita user                                         │
│     Output: { primary, secondary, tertiary, confidence }            │
│     → Gemini langsung deteksi sampai TERTIARY                       │
│                                                                     │
│  2. GENERATE NARRATIVE reflektif                                    │
│     Input: emosi final + cerita + jawaban user                      │
│     Output: narasi empatik (bukan diagnosis)                        │
│                                                                     │
│  Sisanya BUKAN Gemini.                                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                📦 DATA STATIS (dari Database MySQL)                  │
│                                                                     │
│  • Emotion Wheel (primary → secondary → tertiary) → tabel DB       │
│  • Reflection Questions (pilihan ganda ABCD, 5 soal) → tabel DB    │
│  • Safe framing text → tabel DB atau config                         │
│                                                                     │
│  Hanya ada 1 jenis pertanyaan: Reflection Questions.                │
│  Semua sudah pre-defined di database.                               │
│  Backend tinggal query berdasarkan emotion key.                     │
│  TIDAK perlu panggil Gemini untuk ini.                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND — React.js (:3000)                      │
│                                                                     │
│  ┌────────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ Chat UI    │  │ Story Input  │  │  Question  │  │ Narrative  │  │
│  │ Window     │  │ Area         │  │  Picker    │  │ Display    │  │
│  └────────────┘  └──────────────┘  └────────────┘  └────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST API
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  BACKEND — Node.js/Express (:5000)                  │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Auth     │  │ Session &    │  │ Chat Flow   │  │ Question   │  │
│  │ Module   │  │ History      │  │ Engine      │  │ Engine     │  │
│  └──────────┘  └──────────────┘  └──────┬──────┘  └────────────┘  │
│                                         │                           │
│  ┌──────────────────────────────────────┴────────────────────────┐  │
│  │              Sequelize ORM → MySQL                            │  │
│  │  • users, sessions, chat_messages                             │  │
│  │  • emotion_logs, question_responses                           │  │
│  │  • emotion_wheel (primary→secondary→tertiary)                │  │
│  │  • reflection_questions (ABCD per emotion key)                │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP (internal)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  AI SERVICE — FastAPI (:8000)                        │
│                                                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐    │
│  │ Emotion Detector         │  │ Narrative Generator           │    │
│  │ (from story → tertiary)  │  │ (reflective, non-clinical)   │    │
│  └──────────────────────────┘  └──────────────────────────────┘    │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                  Prompt Templates                             │  │
│  │  • detect_emotion.py   → deteksi sampai tertiary             │  │
│  │  • generate_narrative.py → narasi reflektif                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          ▼                                          │
│                 Google Gemini API (free tier)                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Database Schema (MySQL + Sequelize)

```
┌─────────────────────────────┐
│           users              │
├─────────────────────────────┤
│ id            INT PK AI     │
│ name          VARCHAR(100)  │
│ email         VARCHAR(255)  │  UNIQUE
│ password      VARCHAR(255)  │
│ created_at    DATETIME      │
│ updated_at    DATETIME      │
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌─────────────────────────────┐
│          sessions            │
├─────────────────────────────┤
│ id            INT PK AI     │
│ user_id       INT FK        │──→ users.id
│ flow_state    VARCHAR(50)   │  current step in flow
│ detected_primary   VARCHAR  │  emosi hasil AI detect
│ detected_secondary VARCHAR  │  emosi hasil AI detect
│ detected_tertiary  VARCHAR  │  emosi hasil AI detect
│ final_primary      VARCHAR  │  emosi setelah validasi
│ final_secondary    VARCHAR  │  emosi setelah validasi
│ final_tertiary     VARCHAR  │  emosi setelah validasi
│ status        ENUM          │  'active','completed','abandoned'
│ started_at    DATETIME      │
│ ended_at      DATETIME      │  nullable
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌─────────────────────────────┐    ┌─────────────────────────────┐
│      chat_messages           │    │       emotion_logs           │
├─────────────────────────────┤    ├─────────────────────────────┤
│ id            INT PK AI     │    │ id            INT PK AI     │
│ session_id    INT FK        │    │ session_id    INT FK        │→ sessions
│ role          ENUM          │    │ user_id       INT FK        │→ users
│  'user','bot','system'      │    │ primary_emotion   VARCHAR   │
│ message       TEXT          │    │ secondary_emotion VARCHAR   │
│ message_type  VARCHAR(30)   │    │ tertiary_emotion  VARCHAR   │
│  'text','story','answer'    │    │ confidence    FLOAT         │
│  'narrative'                │    │ source        ENUM          │
│ metadata      JSON          │    │  'ai_detect','validated'    │
│ created_at    DATETIME      │    │ validation_score_primary  INT│
└─────────────────────────────┘    │ validation_score_secondary INT│
               │                   │ validation_score_tertiary INT│
               ▼                   │ narrative     TEXT           │
┌─────────────────────────────┐    │ detected_at   DATETIME      │
│    question_responses        │    └─────────────────────────────┘
├─────────────────────────────┤
│ id            INT PK AI     │
│ session_id    INT FK        │──→ sessions.id
║ emotion_key   VARCHAR(100)  │  "Happy.Proud.Confident" (full path)
│ question_index INT          │  1-5
│ question_text TEXT          │
│ user_answer   CHAR(1)       │  'A','B','C','D'
│ expected_answer CHAR(1)     │  'C' (selalu)
│ is_correct    BOOLEAN       │
│ created_at    DATETIME      │
└─────────────────────────────┘

════════════════════════════════════════════════════════════════════
  TABEL BARU: DATA EMOTION WHEEL + PERTANYAAN (di Database)
════════════════════════════════════════════════════════════════════

┌─────────────────────────────┐
│      emotion_wheel           │  ← Semua data wheel disimpan di DB
├─────────────────────────────┤
│ id            INT PK AI     │
│ primary       VARCHAR(50)   │  'Happy','Sad','Angry','Fearful',...
│ secondary     VARCHAR(50)   │  'Playful','Content','Interested',...
│ tertiary      VARCHAR(50)   │  'Aroused','Cheeky','Free',...
│ created_at    DATETIME      │
└─────────────────────────────┘

Contoh isi:
  { primary: "Happy", secondary: "Playful",   tertiary: "Aroused"    }
  { primary: "Happy", secondary: "Playful",   tertiary: "Cheeky"     }
  { primary: "Happy", secondary: "Content",   tertiary: "Free"       }
  { primary: "Happy", secondary: "Content",   tertiary: "Joyful"     }
  ... dst semua kombinasi

┌──────────────────────────────────┐
│      reflection_questions         │  ← Satu-satunya tabel pertanyaan
├──────────────────────────────────┤
│ id              INT PK AI        │
│ emotion_key     VARCHAR(100)     │  "Happy.Proud.Confident" / "Happy.Accepted.Respected"
│ question_index  INT              │  1-5 (atau jumlah soal per path)
│ question_text   TEXT             │
│ option_a        TEXT             │
│ option_b        TEXT             │
│ option_c        TEXT             │  ← expected answer selalu C
│ option_d        TEXT             │
│ expected_answer CHAR(1)          │  'C'
│ created_at      DATETIME         │
└──────────────────────────────────┘
```

**Penting:**

- Hanya ada **1 jenis pertanyaan**: Reflection Questions (pilihan ganda ABCD)
- **emotion_key = full path emosi** (format: "Primary.Secondary.Tertiary")
- Setiap kombinasi emosi punya pertanyaan unik:
  - "Happy.Proud.Confident" ≠ "Happy.Proud.Powerful"
  - "Happy.Accepted.Respected" ≠ "Happy.Accepted.Valued"
- Tidak ada field `level` lagi — semua pertanyaan untuk tertiary path
- Total per session: **5 soal** (1 set untuk detected emotion path)

---

## 6. Chat Flow — Fokus Storytelling (Sampai Tertiary)

```
USER MASUK KE MENU EMOTION CHECKER
│
▼
╔═══════════════════════════════════════════════════════════════════╗
║ STEP 1: SAFE FRAMING                                             ║
║                                                                   ║
║ Bot: [Pembukaan safe space — dinamis dari backend/template]     ║
║      • Jelaskan tujuan: refleksi bukan diagnosis                 ║
║      • Ciptakan rasa aman untuk user bercerita                   ║
║                                                                   ║
║ [Backend: flow_state = 'SAFE_FRAMING']                           ║
╚═══════════════════════════════════════════════════════════════════╝
│
▼
╔═══════════════════════════════════════════════════════════════════╗
║ STEP 2: STORYTELLING (User Bercerita)                            ║
║                                                                   ║
║ Bot: [Ajakan bercerita — prompt dinamis]                         ║
║      • Ajak user berbagi cerita tanpa judgement                  ║
║                                                                   ║
║ User: [Cerita bebas tentang perasaan/situasi mereka]             ║
║                                                                   ║
║ ┌── AI SERVICE DIPANGGIL ──────────────────────────────────────┐ ║
║ │ POST /api/detect-emotion                                      │ ║
║ │ Gemini deteksi LANGSUNG sampai tertiary:                      │ ║
║ │                                                                │ ║
║ │ Response: {                                                    │ ║
║ │   "primary": "Sad",                                           │ ║
║ │   "secondary": "Lonely",                                     │ ║
║ │   "tertiary": "Isolated",                                    │ ║
║ │   "confidence": 0.82                                          │ ║
║ │ }                                                              │ ║
║ └────────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║ Bot: [Transisi ke validasi — dinamis]                            ║
║      • Terima kasih atas cerita user                             ║
║      • Ajak mulai validasi dengan pertanyaan pilihan ganda       ║
║                                                                   ║
║ [Backend: save emotion_log, flow_state = 'STORY_TOLD']          ║
╚═══════════════════════════════════════════════════════════════════╝
│
▼
╔═══════════════════════════════════════════════════════════════════╗
║ STEP 3: VALIDASI EMOSI — Reflection Questions (ABCD)            ║
║                                                                   ║
║ Backend query DB: WHERE emotion_key = 'Sad.Lonely.Isolated'      ║
║ (langsung load pertanyaan untuk FULL PATH emosi terdeteksi)      ║
║                                                                   ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ Q1: "Akhir-akhir ini, apakah kamu merasa terpisah dari       │ ║
║ │      orang-orang di sekitarmu?"                               │ ║
║ │                                                                │ ║
║ │      A. Tidak, aku merasa dekat dengan mereka                 │ ║
║ │      B. Kadang-kadang saja                                    │ ║
║ │      C. Ya, seperti ada jarak                    ← expected   │ ║
║ │      D. Aku tidak yakin                                       │ ║
║ │                                                                │ ║
║ │ User pilih: [C]                                                │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
║ ...dst Q2-Q5 (semuanya ABCD, spesifik untuk "Sad.Lonely.Isolated")║
║                                                                   ║
║ **Catatan**: Jika detected emotion = "Happy.Proud.Confident",    ║
║ maka pertanyaan akan BERBEDA (bukan pertanyaan untuk Sad).       ║
║                                                                   ║
║ SCORING: Hitung berapa jawaban = C                                ║
║ • 4-5/5 → ✅ Emosi CONFIRMED → lanjut narrative                 ║
║ • 2-3/5 → ⚠️ Kurang cocok → suggest emosi lain dari wheel       ║
║ • 0-1/5 → ❌ SALAH → re-detect / tanya ulang                    ║
║                                                                   ║
║ [Backend: flow_state = 'VALIDATE_EMOTION', save responses+score] ║
╚═══════════════════════════════════════════════════════════════════╝
│
▼ (Emotion confirmed)
╔═══════════════════════════════════════════════════════════════════╗
║ STEP 4: NARRATIVE REFLECTION (Generated by Gemini)               ║
║                                                                   ║
║ ┌── AI SERVICE DIPANGGIL ──────────────────────────────────────┐ ║
║ │ POST /api/generate-narrative                                  │ ║
║ │ Body: {                                                        │ ║
║ │   "emotions": {                                                │ ║
║ │     "primary": "Sad",                                         │ ║
║ │     "secondary": "Lonely",                                    │ ║
║ │     "tertiary": "Isolated"                                    │ ║
║ │   },                                                           │ ║
║ │   "user_story": "cerita user...",                             │ ║
║ │   "validation_score": 5                                       │ ║
║ │ }                                                              │ ║
║ └────────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║ ✅ Bot: [NARASI REFLEKTIF DARI GEMINI — AI-GENERATED]            ║
║    • Empatik, validasi perasaan user                             ║
║    • Kontekstual berdasarkan cerita + emosi terdeteksi           ║
║    • Natural seperti chatbot modern, BUKAN template statis       ║
║                                                                   ║
║ ❌ BUKAN: "Kamu mengalami kecemasan tingkat tinggi."             ║
║                                                                   ║
║ Emosi final: Sad > Lonely > Isolated                             ║
║                                                                   ║
║ [Backend: flow_state = 'NARRATIVE', save narrative]              ║
╚═══════════════════════════════════════════════════════════════════╝
│
▼
╔═══════════════════════════════════════════════════════════════════╗
║ STEP 5: CLOSING                                                   ║
║                                                                   ║
║ Bot: [Penutupan — dinamis]                                       ║
║      • Apresiasi partisipasi user                                ║
║      • Validasi perasaan mereka                                  ║
║      • Welcome untuk sesi berikutnya                             ║
║                                                                   ║
║ [Backend: flow_state = 'COMPLETED', session.status = 'completed']║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 7. Cara Kerja Validasi Emosi (Pertanyaan Spesifik per Path)

```
CERITA USER
    │
    ▼
AI deteksi → { primary: "Happy", secondary: "Proud", tertiary: "Confident" }
    │
    ▼
╔══════════════════════════════════════════════════════════════╗
║ VALIDASI EMOSI — "Happy.Proud.Confident"                         ║
╚══════════════════════════════════════════════════════════════╝
    │
    └─→ 5 Reflection Questions (ABCD)
        Pertanyaan SPESIFIK untuk kombinasi "Happy.Proud.Confident"
        User pilih A/B/C/D untuk setiap soal
        │
        Score 4-5/5 → ✅ "Happy.Proud.Confident" CONFIRMED
        Score 2-3/5 → ⚠️ Suggest emosi lain
        Score 0-1/5 → ❌ Re-detect
    │
    ▼ (confirmed)

EMOSI FINAL = Happy > Proud > Confident
    │
    ▼
NARRATIVE GENERATION (Gemini) → tampilkan ke user
```

**Contoh Perbedaan Pertanyaan:**

| Emotion Path                 | Contoh Pertanyaan                                                       |
| ---------------------------- | ----------------------------------------------------------------------- |
| **Happy.Proud.Confident**    | "Akhir-akhir ini, apakah kamu merasa yakin dengan kemampuanmu?"         |
| **Happy.Accepted.Respected** | "Apakah kamu merasa orang-orang menghargai pendapatmu?"                 |
| **Sad.Lonely.Isolated**      | "Akhir-akhir ini, apakah kamu merasa terpisah dari orang di sekitarmu?" |
| **Angry.Let Down.Betrayed**  | "Apakah ada situasi di mana kamu merasa orang terdekat mengecewakanmu?" |

Setiap path emosi punya set pertanyaan yang **unik dan spesifik**.

**Total pertanyaan per session: 5 soal** (tidak lagi 15 soal bertahap).

---

## 8. API Endpoints

### Backend (Express :5000)

```
AUTH
  POST   /api/auth/register
  POST   /api/auth/login

SESSION
  POST   /api/sessions                      → mulai session baru
  GET    /api/sessions/:id                  → detail session
  PATCH  /api/sessions/:id/end              → akhiri session

CHAT (flow engine)
  POST   /api/chat/message                  → kirim jawaban + terima respons
         Body: { sessionId, answer?, flowState }
         Response: { botMessage, nextFlowState, questions? }

  GET    /api/chat/:sessionId/history       → riwayat chat

EMOTION
  GET    /api/emotions/wheel                → ambil semua emotion wheel dari DB
  GET    /api/emotions/wheel/:primary       → ambil secondary options
  GET    /api/emotions/:sessionId/log       → emotion log per session
  GET    /api/emotions/user/:userId/history  → semua emotion logs user

QUESTIONS (dari DB)
  GET    /api/questions/:emotionKey         → pertanyaan untuk full path (e.g., "Happy.Proud.Confident")
```

### AI Service (FastAPI :8000)

```
POST   /api/detect-emotion
       Body: { text }
       Response: { primary, secondary, tertiary, confidence, reasoning }
       → Gemini deteksi langsung sampai tertiary

POST   /api/generate-narrative
       Body: { emotions, user_story, validation_scores }
       Response: { narrative, tone, key_themes }

GET    /api/health
       Response: { status: "ok", gemini_connected: true }
```

**Catatan:** Tidak ada endpoint `/api/emotion-naming` lagi.
Gemini hanya dipanggil 2x per session: detect + narrative.

---

## 9. Komunikasi Antar Service

```
FRONTEND                     BACKEND                      AI SERVICE
   │                            │                             │
   │ POST /api/chat/message     │                             │
   │ { message: "cerita..." }  │                             │
   │───────────────────────────►│                             │
   │                            │ POST /api/detect-emotion    │
   │                            │ { text: "cerita..." }       │
   │                            │────────────────────────────►│
   │                            │                             │ Gemini call
   │                            │                             │◄──────────►
   │                            │ { primary, secondary,       │
   │                            │   tertiary, confidence }    │
   │                            │◄────────────────────────────│
   │                            │                             │
   │                            │ Save emotion_log to MySQL   │
   │                            │ Query reflection_questions  │
   │                            │ from DB (by emotion_key)    │
   │                            │                             │
   │ { botMessage, questions }  │                             │
   │◄───────────────────────────│                             │
   │                            │                             │
   │ POST /api/chat/message     │                             │
   │ { answer: "C" }           │                             │
   │───────────────────────────►│                             │
   │                            │ Save response, calc score   │
   │                            │ Load next questions from DB │
   │ { botMessage, questions }  │                             │
   │◄───────────────────────────│                             │
   │                            │                             │
   │  ... (repeat per level)    │                             │
   │                            │                             │
   │ (after tertiary confirmed) │                             │
   │                            │ POST /api/generate-narrative│
   │                            │────────────────────────────►│
   │                            │                             │ Gemini call
   │                            │ { narrative }               │
   │                            │◄────────────────────────────│
   │ { botMessage: narrative }  │                             │
   │◄───────────────────────────│                             │
```

---

## 10. Flow States (State Machine)

```
SAFE_FRAMING           → pembuka, safe space framing
STORYTELLING           → user bercerita (free text)
STORY_TOLD             → cerita diterima, AI deteksi emosi
VALIDATE_EMOTION       → 5 reflection questions untuk detected emotion path (ABCD)
NARRATIVE              → Gemini generate narasi reflektif
COMPLETED              → session selesai
```

Backend menyimpan `flow_state` di tabel `sessions`.
Setiap POST /api/chat/message, backend cek state → tentukan step berikutnya.

---

## 11. Chat Memory & Context Management

**Apakah chatbot ini punya memory seperti ChatGPT?**

✅ **Ya, dalam session yang sama:**

```
┌─────────────────────────────────────────────────────────────┐
│ DALAM 1 SESSION (Conversation Memory)                      │
├─────────────────────────────────────────────────────────────┤
│ • Backend menyimpan semua chat_messages per session_id     │
│ • Saat generate narrative, Gemini mendapat:                │
│   - Cerita user (storytelling)                             │
│   - Emosi terdeteksi                                       │
│   - Validation scores                                      │
│ • Frontend bisa tampilkan riwayat chat dalam session       │
│   (GET /api/chat/:sessionId/history)                       │
│ • User bisa scroll up lihat percakapan sebelumnya          │
└─────────────────────────────────────────────────────────────┘
```

⚠️ **Terbatas untuk context narrative:**

- Gemini **hanya dipanggil 2x** per session (detect + narrative)
- Tidak ada "conversational back-and-forth" seperti ChatGPT
- Setelah narrative ditampilkan → session selesai
- Jika user ingin chat lagi → mulai session baru

📊 **Antar session (Historical Memory):**

```
┌─────────────────────────────────────────────────────────────┐
│ CROSS-SESSION HISTORY                                       │
├─────────────────────────────────────────────────────────────┤
│ • User bisa lihat riwayat semua session sebelumnya          │
│   (GET /api/emotions/user/:userId/history)                  │
│ • Data tersimpan: emotion logs, narratives, timestamps      │
│ • Berguna untuk trend analysis (backlog feature)            │
│ • Tapi TIDAK otomatis di-inject ke prompt Gemini            │
│   (berbeda dengan ChatGPT yang selalu ingat chat history)   │
└─────────────────────────────────────────────────────────────┘
```

**Kesimpulan:**

| Fitur                          | Chatbot Ini       | ChatGPT          |
| ------------------------------ | ----------------- | ---------------- |
| Memory dalam 1 session         | ✅ Ya             | ✅ Ya            |
| Conversational multi-turn chat | ❌ Tidak          | ✅ Ya            |
| Riwayat session tersimpan      | ✅ Ya (di DB)     | ✅ Ya            |
| Auto-inject history ke prompt  | ❌ Tidak (manual) | ✅ Ya (otomatis) |
| Flow                           | Linear (5 steps)  | Free-form dialog |

---

### 🔍 Penjelasan: Apa itu "Auto-Inject History ke Prompt"?

**Contoh ChatGPT (Auto-Inject ✅):**

```
User: "Aku lagi sedih"
  ↓
ChatGPT API dipanggil dengan:
  {
    messages: [
      { role: "user", content: "Aku lagi sedih" }
    ]
  }
  ↓
Bot: "Kenapa kamu sedih? Cerita dong"

User: "Karena putus cinta"  ← Message kedua
  ↓
ChatGPT API dipanggil LAGI dengan FULL HISTORY:
  {
    messages: [
      { role: "user", content: "Aku lagi sedih" },        ← HISTORY
      { role: "assistant", content: "Kenapa kamu sedih..." }, ← HISTORY
      { role: "user", content: "Karena putus cinta" }      ← NEW
    ]
  }
  ↓
Bot: "Oh maaf dengar itu. Sudah berapa lama kalian bersama?"
     ↑ Bot "ingat" percakapan sebelumnya karena history otomatis dikirim
```

**Chatbot Ini (Manual/Tidak Auto-Inject ❌):**

```
User: [Bercerita panjang tentang perasaannya]
  ↓
Gemini API Call #1: Detect Emotion
  {
    text: "cerita user..."
  }
  ↓ hanya cerita, TIDAK include chat history sebelumnya

Response: { primary: "Sad", secondary: "Lonely", tertiary: "Isolated" }

↓ (User jawab 5 pertanyaan validasi)

Gemini API Call #2: Generate Narrative
  {
    user_story: "cerita user...",
    emotions: { primary: "Sad", secondary: "Lonely", tertiary: "Isolated" },
    validation_score: 5
  }
  ↓ hanya data yang DIPILIH manual, bukan semua chat history

Response: { narrative: "Dalam beberapa waktu terakhir..." }

↓ Session SELESAI, tidak ada bolak-balik lagi
```

**Perbedaan Kunci:**

| Aspek                          | ChatGPT                                        | Chatbot Ini                                               |
| ------------------------------ | ---------------------------------------------- | --------------------------------------------------------- |
| **Setiap user ngirim pesan**   | API dipanggil + SEMUA history dikirim otomatis | API hanya dipanggil 2x (detect + narrative)               |
| **Context yang dikirim ke AI** | Full conversation history                      | Hanya data spesifik (cerita + emosi)                      |
| **Jumlah API call**            | Banyak (setiap message)                        | Cuma 2x per session                                       |
| **Bot "ingat" percakapan**     | Ya, otomatis                                   | Cukup untuk generate narrative, tapi tidak conversational |

**Kenapa chatbot ini tidak auto-inject?**

✅ **Keuntungan:**

- Lebih murah (Gemini cuma dipanggil 2x)
- Flow terkontrol (tidak perlu handle edge case conversational)
- Fokus ke tujuan: detect emosi → validate → narrative

❌ **Trade-off:**

- Tidak bisa tanya-jawab bebas seperti ChatGPT
- User tidak bisa "lanjutin" percakapan setelah narrative

**Jika ingin fitur conversational seperti ChatGPT:**  
Bisa ditambahkan nanti dengan:

- Socket.IO untuk real-time streaming
- Context window management (inject chat history ke Gemini prompt setiap request)
- Flow state yang lebih fleksibel (bukan linear)

→ Masuk backlog sebagai **"Conversational Mode"**

---

## 12. Folder Structure (Dengan Penjelasan Peran)

```
mhcm-chatbot/
│
├── frontend/                              # ══ REACT.JS (TypeScript) ══
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatWindow.tsx         # Container utama chat, render daftar pesan
│   │   │   │   ├── MessageBubble.tsx      # Satu bubble pesan (user/bot), styling beda per role
│   │   │   │   ├── ChatInput.tsx          # Input box untuk cerita user (step storytelling)
│   │   │   │   └── TypingIndicator.tsx    # Animasi "bot sedang mengetik..."
│   │   │   ├── Questions/
│   │   │   │   └── QuestionCard.tsx       # Kartu pilihan ganda ABCD, reusable untuk semua level
│   │   │   ├── Narrative/
│   │   │   │   └── NarrativeDisplay.tsx   # Tampilkan narasi reflektif dari Gemini, styling khusus
│   │   │   └── Layout/
│   │   │       ├── Header.tsx             # Navbar atas, judul app, tombol session baru
│   │   │       └── MainLayout.tsx         # Layout wrapper (header + content area)
│   │   ├── pages/
│   │   │   ├── HomePage.tsx               # Landing page, tombol "Mulai Emotion Checker"
│   │   │   ├── ChatPage.tsx               # Halaman utama chat, orchestrate semua component
│   │   │   └── HistoryPage.tsx            # Riwayat session & emotion logs user
│   │   ├── hooks/
│   │   │   ├── useChat.ts                 # Custom hook: kirim pesan, terima response, kelola state chat
│   │   │   └── useSession.ts             # Custom hook: mulai/akhiri session, track flow state
│   │   ├── services/
│   │   │   └── api.ts                     # Axios instance + semua API calls ke backend
│   │   ├── types/
│   │   │   └── index.ts                   # TypeScript interfaces: Message, Session, Question, Emotion
│   │   └── App.tsx                        # Root component, routing (React Router)
│   ├── package.json
│   └── tailwind.config.js                 # Konfigurasi Tailwind CSS theme & colors
│
├── backend/                               # ══ NODE.JS + EXPRESS ══
│   ├── src/
│   │   ├── config/
│   │   │   └── database.js               # Koneksi Sequelize ke MySQL, config pool & dialect
│   │   ├── models/
│   │   │   ├── index.js                   # Sequelize init, import semua model, define associations
│   │   │   ├── User.js                    # Model user: id, name, email, password
│   │   │   ├── Session.js                # Model session: flow_state, detected/final emotions, status
│   │   │   ├── ChatMessage.js            # Model pesan chat: role, message, message_type, metadata
│   │   │   ├── EmotionLog.js             # Model log emosi: primary/secondary/tertiary, scores, narrative
│   │   │   ├── QuestionResponse.js       # Model jawaban user: emotion_key, answer (A/B/C/D), is_correct
│   │   │   ├── ReflectionQuestion.js     # Model reflection questions: ABCD options per emotion_key
│   │   │   └── EmotionWheel.js           # Model emotion wheel: primary → secondary → tertiary mapping
│   │   ├── controllers/
│   │   │   ├── authController.js          # Register, login, JWT token generation
│   │   │   ├── chatController.js          # Terima pesan/jawaban, panggil flowEngine, return response
│   │   │   ├── sessionController.js       # Buat session baru, get session, end session
│   │   │   └── emotionController.js       # Get emotion wheel, get emotion logs, get history
│   │   ├── routes/
│   │   │   └── index.js                   # Semua route definitions, mapping URL → controller
│   │   ├── services/
│   │   │   ├── flowEngine.js              # STATE MACHINE: cek flow_state → tentukan step berikutnya
│   │   │   ├── questionEngine.js          # Query pertanyaan dari DB by emotion_key + level
│   │   │   ├── scoringEngine.js           # Hitung score jawaban ABCD, tentukan confirmed/re-detect
│   │   │   └── aiClient.js               # HTTP client ke FastAPI AI Service (axios)
│   │   ├── seeders/
│   │   │   ├── emotionWheelSeeder.js      # Seed semua data emotion wheel ke DB
│   │   │   └── reflectionQuestionsSeeder.js # Seed semua reflection questions ke DB
│   │   ├── middleware/
│   │   │   ├── auth.js                    # JWT verification middleware
│   │   │   └── errorHandler.js            # Global error handler, format error response
│   │   └── app.js                         # Express app init, middleware setup, mount routes
│   ├── package.json
│   └── .sequelizerc                       # Sequelize CLI config: paths untuk models, seeders, migrations
│
├── ai-service/                            # ══ PYTHON + FASTAPI ══
│   ├── app/
│   │   ├── main.py                        # FastAPI app init, mount routes, CORS config
│   │   ├── config.py                      # Gemini API key, model name, settings
│   │   ├── routes/
│   │   │   ├── emotion_routes.py          # POST /api/detect-emotion endpoint
│   │   │   └── narrative_routes.py        # POST /api/generate-narrative endpoint
│   │   ├── services/
│   │   │   ├── gemini_client.py           # Wrapper Google Gemini API: init model, send prompt, parse
│   │   │   ├── emotion_detector.py        # Kirim cerita ke Gemini → parse primary/secondary/tertiary
│   │   │   └── narrative_generator.py     # Kirim emosi+cerita ke Gemini → return narasi reflektif
│   │   ├── prompts/
│   │   │   ├── detect_emotion.py          # Prompt template: "Analisis cerita, deteksi emosi sampai tertiary"
│   │   │   └── generate_narrative.py      # Prompt template: "Buat narasi reflektif, bukan diagnosis"
│   │   └── schemas/
│   │       └── models.py                  # Pydantic models: request/response schemas
│   ├── requirements.txt                   # Dependencies: fastapi, uvicorn, google-generativeai, pydantic
│   └── Dockerfile                         # Container image untuk AI service
│
├── docker-compose.yml                     # Orchestrate 3 services + MySQL
├── .gitignore
└── README.md                              # ← File ini
```

---

## 13. Yang Belum Termasuk (Backlog)

| Feature                            | Status    | Catatan                               |
| ---------------------------------- | --------- | ------------------------------------- |
| Trend-Aware Response (time series) | ⏳ Nanti  | Butuh data history dulu, tambah nanti |
| Emotion Wheel visual UI (D3/chart) | ⏳ Nanti  | Bisa tambah setelah core flow jalan   |
| WebSocket real-time chat           | ⏳ Nanti  | REST dulu cukup                       |
| User authentication (JWT)          | ⏳ Nanti  | Bisa anonymous dulu                   |
| Rate limiting Gemini calls         | ⏳ Nanti  | Free tier ada limit                   |
| Deploy (Docker/Cloud)              | ⏳ Nanti  | Lokal dulu                            |
| Seed semua data emosi ke DB        | 🔜 Segera | Dari spreadsheet Excel yang sudah ada |

---

_Document ini adalah brief arsitektur v3.0 (revisi).
Belum ada kode. Data emotion wheel dari spreadsheet akan di-seed ke DB saat implementasi._

_Perubahan v3.0:_

- Pertanyaan spesifik per **full emotion path** (bukan per level)
- Chat **memory dalam session** (seperti ChatGPT, tapi linear flow)
- Total pertanyaan: **5 soal** per session (bukan 15 bertahap)
- Flow disederhanakan: 5 steps (bukan 7)

_Selanjutnya: implementasi dimulai dari service mana dulu?_
