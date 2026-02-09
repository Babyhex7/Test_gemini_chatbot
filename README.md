# MHCM Chatbot — Architecture Brief Document

> Mental Health Conversational Mirror — Emotion Checker via Storytelling
> **Versi: 4.1 (Creative Narrative & DB Personalization)** | Tanggal: 9 Februari 2026

---

## 1. Ringkasan Produk

Chatbot refleksi emosi berbasis storytelling. User bercerita tentang kejadian/perasaannya,
lalu sistem mendeteksi emosi, memvalidasi lewat **pertanyaan refleksi (pilihan ganda ABCD)**
yang spesifik untuk **kombinasi emosi lengkap**, dan menghasilkan **narasi reflektif yang panjang, kreatif, dan personal** — **bukan diagnosis klinis**.

**Prinsip Utama:**

- Refleksi, bukan diagnosis
- Bahasa manusiawi, bukan label klinis
- User bercerita → sistem merespons dengan empati **dan kreativitas**
- Pertanyaan follow-up spesifik untuk **setiap path emosi** (e.g., Happy.Proud.Confident vs Happy.Accepted.Respected)
- **Chat memory**: sistem ingat konteks percakapan dalam session DAN **cross-session history** (journey awareness)
- **Personalized narrative**: Gemini membaca data dari database untuk respons yang **personal dan journey-aware**
- **Creative narrative**: Gemini diberi kebebasan menulis panjang dan kreatif, tidak dibatasi template kaku
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
│  1. DETECT EMOTION dari cerita user + HISTORY CONTEXT               │
│     Input: teks cerita user + ringkasan 5 session terakhir          │
│     Output: { primary, secondary, tertiary, confidence, notes }     │
│     → Gemini deteksi sampai TERTIARY dengan awareness trend user    │
│                                                                     │
│  2. GENERATE NARRATIVE reflektif + PERSONALIZED + CREATIVE          │
│     Input: emosi final + cerita lengkap + skor validasi + HISTORY   │
│     Output: narasi PANJANG, mendalam, empatik, journey-aware        │
│                                                                     │
│     ⭐ NARRATIVE TIDAK DIBATASI PANJANGNYA                          │
│     → Gemini diberi kebebasan menulis sekreatif mungkin             │
│     → Boleh pakai metafora, analogi, storytelling balik             │
│     → Fokus: refleksi mendalam, bukan ringkasan singkat             │
│     → Tujuan: user merasa benar-benar didengar dan dipahami         │
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
│ story_text    TEXT          │  cerita user (full)
│ story_summary VARCHAR(200)  │  ringkasan cerita untuk inject history
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
  POST   /api/sessions                      → mulai session baru (+ load history)
  GET    /api/sessions/:id                  → detail session
  PATCH  /api/sessions/:id/end              → akhiri session (+ save story_summary)

CHAT (flow engine)
  POST   /api/chat/message                  → kirim jawaban + terima respons
         Body: { sessionId, answer?, flowState }
         Response: { botMessage, nextFlowState, questions? }

  GET    /api/chat/:sessionId/history       → riwayat chat dalam session

HISTORY (untuk memory inject)
  GET    /api/history/:userId               → 5 session terakhir user (formatted untuk prompt)
  GET    /api/history/:userId/raw           → raw session data (untuk frontend display)

EMOTION
  GET    /api/emotions/wheel                → ambil semua emotion wheel dari DB
  GET    /api/emotions/wheel/:primary       → ambil secondary options
  GET    /api/emotions/:sessionId/log       → emotion log per session
  GET    /api/emotions/user/:userId/history  → semua emotion logs user (trend analysis)

QUESTIONS (dari DB)
  GET    /api/questions/:emotionKey         → pertanyaan untuk full path (e.g., "Happy.Proud.Confident")
```

### AI Service (FastAPI :8000)

```
POST   /api/detect-emotion
       Body: {
         text: "cerita user...",
         history_context: "Previous sessions:\n• Feb 5: SAD.LONELY..."  ← 🆕
       }
       Response: { primary, secondary, tertiary, confidence, journey_note }
       → Gemini deteksi dengan awareness journey user

POST   /api/generate-narrative
       Body: {
         emotions: { primary, secondary, tertiary },
         user_story: "...",
         validation_scores: 5,
         history_context: "Previous sessions:\n..."  ← 🆕
       }
       Response: { narrative, journey_acknowledgment, tone }
       → Gemini generate narrative journey-aware

GET    /api/health
       Response: { status: "ok", gemini_connected: true }
```

**Catatan:**

- Gemini dipanggil 2x per session dengan history context
- Backend query history dari DB → format → kirim ke AI Service

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

## 11. Chat Memory & Context Management (Memory Inject)

**Apakah chatbot ini punya memory? ✅ YA — Cross-Session History Inject**

### 📍 Arsitektur Memory

Chatbot ini menggunakan pendekatan **Memory Inject**: data dari database di-inject ke prompt Gemini sehingga AI "sadar" siapa user dan perjalanan emosionalnya.

**Dalam 1 Session:**

- Backend menyimpan semua chat_messages per session_id
- Cerita user disimpan di `sessions.story_text`
- Saat generate narrative → seluruh konteks dikirim ke Gemini

**Antar Session (Journey Awareness):**

- Backend query 5 session terakhir user dari database
- Format jadi ringkasan: tanggal + emosi + summary cerita
- Inject ke prompt Gemini → AI tahu "perjalanan" user
- Narrative jadi personal: "Senang lihat kamu improve dari kemarin"

### 🔄 Alur Data: Database → Gemini

```
┌─────────────────────────────────────────────────────────────────────┐
│ DATABASE (MySQL via Sequelize)                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  sessions                                                           │
│  ├── final_primary, final_secondary, final_tertiary                │
│  ├── story_summary (ringkasan cerita untuk inject)                 │
│  └── ended_at                                                       │
│                                                                     │
│  emotion_logs                                                       │
│  ├── primary_emotion, secondary_emotion, tertiary_emotion          │
│  ├── confidence                                                     │
│  └── narrative (narasi yang sudah digenerate)                      │
│                                                                     │
│  users                                                              │
│  └── name (untuk personalisasi panggilan)                          │
│                                                                     │
└────────────────────────────────────┬────────────────────────────────┘
                                     │ Backend query & format
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ CONTEXT STRING (yang di-inject ke prompt Gemini)                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  user_context:                                                      │
│  ├── Nama user                                                      │
│  ├── Total sesi sebelumnya                                         │
│  └── Jenis user (new/returning)                                    │
│                                                                     │
│  journey_context:                                                   │
│  ├── Tanggal + emosi + ringkasan cerita (5 sesi terakhir)         │
│  ├── Pola yang terdeteksi (trending up/down, recurring emotion)    │
│  └── Catatan khusus (kalau ada tema berulang)                      │
│                                                                     │
│  current_context:                                                   │
│  ├── Cerita lengkap user sesi ini                                  │
│  ├── Emosi yang terdeteksi + confidence                            │
│  └── Skor validasi (5 soal ABCD)                                   │
│                                                                     │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ GEMINI PROMPT (dengan semua context di atas)                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 📊 Perbandingan: Tanpa vs Dengan History Inject

| Aspek                 | TANPA History Inject             | DENGAN History Inject (arsitektur ini)             |
| --------------------- | -------------------------------- | -------------------------------------------------- |
| **Narrative**         | Generic: "Kamu merasa senang..." | Personal: "Senang lihat kamu improve dari kemarin" |
| **Context**           | Hanya cerita current session     | Cerita + 5 session terakhir + profil user          |
| **Journey Awareness** | ❌ Tidak tahu trend              | ✅ Tahu user naik/turun emotionally                |
| **Empati**            | Standar                          | Deep & personal (journey-aware)                    |
| **User Experience**   | Functional                       | Meaningful & memorable                             |

---

## 11.1 Prompt Template Philosophy — Narrative Generation

**Prinsip utama: Gemini adalah "teman bijak" yang mendengar, bukan psikolog yang mendiagnosis.**

### 🎯 Tujuan Narrative

Narrative bukan sekedar menjelaskan emosi yang terdeteksi. Narrative adalah **refleksi mendalam** yang:

- Menemani user memahami dirinya sendiri
- Mengakui perjalanan emosional user (kalau ada history)
- Memvalidasi perasaan tanpa menghakimi
- Memberikan insight tanpa menggurui
- Menawarkan perspektif tanpa memaksa
- Menggunakan bahasa yang hangat dan personal

### 📝 Elemen Prompt Template untuk Narrative

**1. Role Definition (Siapa Gemini dalam konteks ini)**

- Teman yang bijak dan hangat, bukan terapis
- Pendengar yang penuh empati
- Seseorang yang menghargai keberanian user untuk bercerita
- Tidak memberikan diagnosis atau saran klinis

**2. User Context Injection (Data dari database)**

- Nama user (untuk personalisasi)
- Jumlah sesi sebelumnya (new user vs returning user)
- History 5 sesi terakhir (tanggal, emosi, ringkasan cerita)
- Pola yang muncul (kalau ada: recurring theme, trend)

**3. Current Session Context**

- Cerita lengkap user di sesi ini
- Emosi yang terdeteksi (primary.secondary.tertiary)
- Tingkat confidence deteksi
- Skor validasi (berapa soal dijawab benar)

**4. Output Instructions (Bagaimana narrative ditulis)**

- Panjang: Tidak dibatasi, tulis selengkap yang dirasa perlu
- Gaya: Conversational, hangat, personal
- Struktur: Bebas mengalir, tidak perlu bullet points
- Boleh pakai emoji secukupnya untuk kehangatan
- Akui journey kalau ada history
- Validasi perasaan sebelum memberikan perspektif
- Akhiri dengan sentiment positif atau kata-kata supportive

### 🌟 Filosofi Narrative Panjang

Narrative diharapkan **panjang dan mendalam** karena:

1. **User sudah invest waktu bercerita** → respons singkat terasa tidak menghargai
2. **Emosi itu kompleks** → perlu penjelasan yang nuanced
3. **Ini bukan FAQ bot** → ini companion yang menemani refleksi
4. **Personalisasi butuh ruang** → mengakui journey butuh beberapa kalimat
5. **Closure yang bermakna** → user perlu merasa "didengar sepenuhnya"

### 📋 Komponen Narrative yang Diharapkan

**Untuk User Baru (Belum Ada History):**

- Apresiasi keberanian bercerita
- Refleksi mendalam tentang emosi yang terdeteksi
- Penjelasan mengapa emosi itu masuk akal dalam konteks ceritanya
- Validasi: perasaan itu wajar dan valid
- Insight: apa yang mungkin sedang terjadi dalam diri user
- Perspektif: cara lain melihat situasi (tanpa menggurui)
- Penutup: kata-kata supportive dan encouraging

**Untuk Returning User (Ada History):**

- Semua komponen di atas, PLUS:
- Acknowledgment journey: "Terakhir kali kamu merasakan X, sekarang Y..."
- Pattern recognition: "Aku lihat ada pola..." (kalau ada)
- Progress celebration: "Ini perkembangan yang positif..." (kalau membaik)
- Empathy for struggle: "Aku mengerti ini masih berat..." (kalau masih sama/memburuk)
- Continuity: merasa seperti percakapan berkelanjutan, bukan sesi terisolasi

### 🎨 Kreativitas Narrative

Gemini diberi kebebasan untuk:

- Menggunakan metafora yang relevan dengan cerita user
- Membuat analogi yang membantu user memahami emosinya
- Menyisipkan pertanyaan retoris untuk refleksi lebih dalam
- Menggunakan storytelling balik (menggambarkan ulang situasi user dengan perspektif baru)
- Memberikan "nama" pada perasaan yang mungkin sulit diungkapkan user

**Yang Tidak Boleh:**

- Memberikan diagnosis (ini bukan klinis)
- Menyarankan terapi/profesional help (kecuali user explicitly butuh)
- Menghakimi keputusan atau perasaan user
- Memberikan solusi langsung (ini tentang refleksi, bukan problem-solving)
- Terlalu pendek atau generik

---

## 11.2 Struktur Prompt Template — Detect Emotion

Prompt untuk deteksi emosi berisi:

**Bagian 1: Role & Context**

- Gemini bertindak sebagai emotion analyst yang sensitif dan nuanced
- Paham Feeling Wheel taxonomy (7 primary → secondary → tertiary)
- Aware bahwa user punya journey (kalau ada history)

**Bagian 2: User Journey Injection**

- History 5 session terakhir (tanggal, emosi, ringkasan cerita)
- Pattern yang terdeteksi ("recurring anxiety", "trending better", dll)
- Kalau new user: statement bahwa ini user baru

**Bagian 3: Current Story**

- Cerita lengkap yang ditulis user di sesi ini
- Tidak dipotong atau diringkas

**Bagian 4: Output Format**

- Primary emotion (dari 7 opsi: Happy, Sad, Angry, Fearful, Surprised, Disgusted, Bad)
- Secondary emotion (spesifik ke primary)
- Tertiary emotion (paling spesifik)
- Confidence score (0.0 - 1.0)
- Journey note (observasi tentang pattern, kalau relevan)

---

## 11.3 Struktur Prompt Template — Generate Narrative

**Ini adalah prompt paling penting di sistem — menghasilkan output yang user lihat dan rasakan.**

### Bagian 1: Role Definition

Gemini diminta menjadi:

- Sahabat yang bijak dan hangat
- Pendengar yang penuh perhatian
- Seseorang yang menghargai keberanian bercerita
- BUKAN terapis, BUKAN psikolog, BUKAN counselor
- Tujuan: menemani refleksi, bukan memberikan diagnosis

### Bagian 2: User Profile Injection

Data dari database yang di-inject:

- Nama user (untuk personalisasi panggilan)
- Status: new user atau returning user
- Jumlah sesi sebelumnya
- Kalau returning: ringkasan 5 sesi terakhir dengan:
  - Tanggal session
  - Emosi yang terdeteksi (full path)
  - Ringkasan singkat cerita

### Bagian 3: Current Session Data

- Cerita lengkap user di sesi ini (tidak dipotong)
- Emosi yang terdeteksi: primary.secondary.tertiary
- Confidence level deteksi AI
- Hasil validasi: skor dari 5 pertanyaan ABCD
- Journey note dari deteksi (kalau ada pattern)

### Bagian 4: Narrative Instructions

Gemini diberitahu untuk:

**Panjang & Kedalaman:**

- Tulis selengkap dan sepanjang yang dirasa perlu
- Tidak ada batasan kata — kualitas lebih penting dari kuantitas
- Ini BUKAN summary atau ringkasan cepat
- User sudah invest waktu bercerita → respons harus setimpal

**Struktur yang Diharapkan:**

- Pembukaan hangat yang menyapa user secara personal
- Acknowledgment journey (kalau returning user)
- Refleksi tentang cerita yang diceritakan user
- Penjelasan tentang emosi yang terdeteksi dalam konteks ceritanya
- Validasi: mengapa perasaan itu masuk akal dan valid
- Insight: apa yang mungkin sedang terjadi dalam diri user
- Perspektif alternatif (TANPA menggurui)
- Penutup yang warm dan encouraging

**Gaya Bahasa:**

- Bahasa Indonesia yang natural, seperti ngobrol dengan teman
- Boleh pakai emoji secukupnya untuk kehangatan (tidak berlebihan)
- Personal: sebut nama user, refer ke cerita spesifik mereka
- Hindari bahasa klinis atau jargon psikologi
- Hindari bullet points — tulis mengalir seperti surat

**Kreativitas:**

- Boleh pakai metafora yang relevan dengan cerita user
- Boleh pakai analogi untuk menjelaskan emosi
- Boleh sisipkan pertanyaan retoris untuk refleksi
- Boleh "ceritakan ulang" situasi user dengan framing baru
- Boleh kasih "nama" pada perasaan yang sulit diungkapkan

**Yang Tidak Boleh:**

- Diagnosis (ini bukan klinis)
- Saran untuk cari bantuan profesional (kecuali diminta)
- Menghakimi keputusan atau perasaan
- Solusi langsung atau problem-solving
- Terlalu singkat atau generik
- Copy-paste template yang sama untuk semua user

### Bagian 5: Output Expectations

Gemini menghasilkan:

- Narrative text: string panjang berisi refleksi
- Journey acknowledged: boolean
- Key insights: array of strings (untuk internal logging)

---

## 11.4 Contoh Output Narrative yang Diharapkan

**Skenario:** Returning user (4 sesi sebelumnya), cerita tentang keberhasilan kecil

**❌ Narrative yang TIDAK diinginkan (terlalu pendek/generik):**

> Kamu merasa senang! Itu emosi yang positif. Terus pertahankan ya.

**✅ Narrative yang DIINGINKAN (personal, mendalam, journey-aware):**

> Hai [Nama]! Terima kasih sudah kembali berbagi cerita hari ini. Senang sekali mendengar kabar baik darimu kali ini.
>
> Kalau aku lihat ke belakang, perjalananmu beberapa hari terakhir cukup intens ya. Dari perasaan kesepian setelah pindah kota, lalu rindu yang dalam pada teman-teman lama, kemudian kekhawatiran soal adaptasi... dan sekarang kamu datang dengan cerita yang berbeda. Kamu cerita tentang [detail spesifik dari cerita user].
>
> Ada sesuatu yang menarik yang aku tangkap dari ceritamu. Perasaan "diterima" yang kamu rasakan ini — itu bukan sesuatu yang datang begitu saja. Itu adalah hasil dari keberanianmu untuk membuka diri, meskipun sebelumnya ada keraguan dan ketakutan. Kamu memilih untuk tetap mencoba, tetap hadir, tetap memberi kesempatan pada orang-orang baru untuk mengenalmu.
>
> Emosi yang kamu rasakan sekarang — _valued_, merasa dihargai dan punya tempat — itu adalah buah dari proses yang sudah kamu jalani. Kadang kita lupa bahwa perasaan nyaman itu butuh waktu untuk tumbuh. Dan kamu sudah memberikan waktu itu pada dirimu sendiri.
>
> Yang membuatku terkesan adalah bagaimana kamu menceritakan momen [detail spesifik]. Ada kebanggaan yang tersirat di sana, meski mungkin kamu sendiri tidak sadar. Itu sah banget untuk dimiliki dan dirayakan.
>
> Perjalanan emosi dari minggu kemarin ke hari ini menunjukkan sesuatu tentang dirimu — bahwa kamu punya resilience yang mungkin kadang kamu remehkan sendiri. Dari titik terendah kemarin, kamu tidak stuck di sana. Kamu terus bergerak.
>
> Ke depan, ingat bahwa perasaan nyaman ini bukan berarti tidak akan ada hari yang berat lagi. Tapi sekarang kamu tahu bahwa kamu mampu melaluinya. Dan kalau sewaktu-waktu perlu berbagi cerita lagi, aku di sini. 💙

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
│   │   │   ├── Journey/
│   │   │   │   └── JourneyPanel.tsx       # 🆕 Panel sidebar: ringkasan perjalanan emosi sebelumnya
│   │   │   └── Layout/
│   │   │       ├── Header.tsx             # Navbar atas, judul app, tombol session baru
│   │   │       └── MainLayout.tsx         # Layout wrapper (header + content area)
│   │   ├── pages/
│   │   │   ├── HomePage.tsx               # Landing page, tombol "Mulai Emotion Checker"
│   │   │   ├── ChatPage.tsx               # Halaman utama chat, orchestrate semua component
│   │   │   └── HistoryPage.tsx            # Riwayat session & emotion logs user
│   │   ├── hooks/
│   │   │   ├── useChat.ts                 # Custom hook: kirim pesan, terima response, kelola state chat
│   │   │   ├── useSession.ts              # Custom hook: mulai/akhiri session, track flow state
│   │   │   └── useHistory.ts              # 🆕 Custom hook: fetch journey/history untuk display sidebar
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
│   │   │   ├── historyService.js          # 🆕 Query & format session history untuk inject ke prompt
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
│   │   │   ├── emotion_detector.py        # Kirim cerita+history ke Gemini → parse emotion + journey note
│   │   │   └── narrative_generator.py     # Kirim emosi+cerita+history → narasi PANJANG + KREATIF
│   │   ├── prompts/
│   │   │   ├── detect_emotion.py          # Prompt template deteksi emosi (dengan history inject)
│   │   │   └── generate_narrative.py      # ⭐ Prompt template narasi PANJANG, KREATIF, PERSONALIZED
│   │   │                                  # → Tidak ada batasan panjang
│   │   │                                  # → Bebas metafora, analogi, storytelling
│   │   │                                  # → User profile + journey dari DB di-inject
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

## 13. Yang Belum Termasuk (Backlog & Roadmap)

### ✅ MVP Phase 1 (Sekarang) — History Inject

| Feature                        | Status      | Catatan                                    |
| ------------------------------ | ----------- | ------------------------------------------ |
| Cross-session history inject   | ✅ Termasuk | Query 5 session → inject ke Gemini prompt  |
| Personalized narrative         | ✅ Termasuk | Journey-aware: "Senang lihat kamu improve" |
| Emotion detection with context | ✅ Termasuk | Gemini tahu trend emosi user sebelumnya    |
| Seed semua data emosi ke DB    | 🔜 Segera   | Dari spreadsheet Excel yang sudah ada      |
| User authentication (JWT)      | 🔜 Segera   | Untuk identifikasi user & session history  |

### 🔜 Phase 2 (Nanti) — RAG untuk Resource Personalization

| Feature                            | Status     | Catatan                                    |
| ---------------------------------- | ---------- | ------------------------------------------ |
| RAG untuk PDF psychology resources | ⏳ Phase 2 | Retrieve artikel relevan berdasarkan emosi |
| Vector DB (Chroma/Pinecone)        | ⏳ Phase 2 | Embed & store psychology articles          |
| Resource recommendation            | ⏳ Phase 2 | "Artikel ini cocok untuk kondisimu..."     |

### ⏳ Phase 3 (Future) — LangChain Refactor

| Feature                  | Status     | Catatan                                   |
| ------------------------ | ---------- | ----------------------------------------- |
| LangChain PromptTemplate | ⏳ Phase 3 | Cleaner prompt management                 |
| LangChain OutputParser   | ⏳ Phase 3 | Auto-validate JSON output dengan Pydantic |
| LangChain Memory         | ⏳ Phase 3 | Automatic context management              |

### 📦 Backlog (Nice to Have)

| Feature                       | Status   | Catatan                              |
| ----------------------------- | -------- | ------------------------------------ |
| Trend-Aware Visual (D3 Chart) | ⏳ Nanti | Visualisasi journey emosi user       |
| Emotion Wheel visual UI       | ⏳ Nanti | Interactive wheel untuk review       |
| WebSocket real-time chat      | ⏳ Nanti | Typing indicator, streaming response |
| Rate limiting Gemini calls    | ⏳ Nanti | Free tier ada limit                  |
| Deploy (Docker/Cloud)         | ⏳ Nanti | Lokal dulu                           |

---

## 14. Roadmap Timeline

```
┌─────────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT ROADMAP                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ PHASE 1: MVP dengan History Inject (Sekarang)                      │
│ ═══════════════════════════════════════════════                    │
│ Minggu 1-4:  Setup backend, DB schema, models                      │
│ Minggu 5-6:  AI Service (detect + narrative dengan history)        │
│ Minggu 7-8:  Flow engine, history inject logic                     │
│ Minggu 9-10: Frontend chat UI                                       │
│ Minggu 11-12: Testing, seed data, polish                            │
│                                                                     │
│ → LAUNCH MVP v1.0 (3 bulan)                                         │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ PHASE 2: RAG untuk Resources (Setelah MVP stabil)                  │
│ ═══════════════════════════════════════════════════                │
│ Minggu 13-14: Setup Chroma vector DB                                │
│ Minggu 15-16: Embed psychology PDFs                                 │
│ Minggu 17-18: Integrate retriever ke narrative                      │
│                                                                     │
│ → LAUNCH v2.0 dengan Resource Recommendation (+6 minggu)           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ PHASE 3: LangChain Refactor (Setelah RAG jalan)                    │
│ ═══════════════════════════════════════════════════                │
│ Minggu 19-20: Refactor prompts ke PromptTemplate                   │
│ Minggu 21-22: Add OutputParsers, Memory abstraction                │
│                                                                     │
│ → LAUNCH v3.0 dengan Clean Architecture (+4 minggu)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

_Document ini adalah brief arsitektur v4.0 (Memory Inject).
Belum ada kode. Data emotion wheel dari spreadsheet akan di-seed ke DB saat implementasi._

_Perubahan v4.0:_

- ✅ **Cross-session history inject**: Gemini menerima 5 session terakhir
- ✅ **Personalized narrative**: Journey-aware responses
- ✅ **Emotion detection with context**: Gemini tahu trend user
- ✅ Database schema: Tambah `story_text` & `story_summary` di sessions
- ✅ Backend: Tambah `historyService.js` untuk query & format history
- ✅ AI Service: Update prompts untuk menerima history context
- ✅ Roadmap: Phase 1 (MVP) → Phase 2 (RAG) → Phase 3 (LangChain)

_Selanjutnya: implementasi dimulai dari Backend (historyService + models)_
