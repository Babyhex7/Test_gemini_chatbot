# 🧠 EduMindAI - Chatbot Pendamping Reflektif Emosional

> Chatbot pendamping reflektif awal (**front-door**) dalam ekosistem wellness sekolah. Membantu siswa menamai emosi, melakukan refleksi ringan & aman, dan memahami kapan perlu dukungan manusia — menggunakan **Google Gemini API**.

---

## 📋 Daftar Isi

- [Gambaran Umum](#-gambaran-umum)
- [Fitur Utama](#-fitur-utama)
- [Alur Sistem — 4 Fase Percakapan](#-alur-sistem--4-fase-percakapan)
- [Arsitektur](#-arsitektur)
- [Struktur Project](#-struktur-project)
- [Tech Stack](#-tech-stack)
- [Dependensi](#-dependensi)
- [Instalasi](#-instalasi)
- [Konfigurasi](#-konfigurasi)
- [API Endpoints](#-api-endpoints)
- [Detail Module](#-detail-module)
- [Alur Chat Detail — Multi-Turn](#-alur-chat-detail--multi-turn)
- [API Design Best Practices](#-api-design-best-practices)
- [Database Schema](#-database-schema-postgresql--sqlalchemy)
- [Struktur Knowledge Base](#-struktur-knowledge-base)
- [Checklist Implementasi](#-checklist-implementasi)

---

## 🎯 Gambaran Umum

**EduMindAI** adalah chatbot pendamping reflektif awal (**front-door**) dalam ekosistem wellness sekolah. Bukan alat diagnosis, terapi, atau pengambil keputusan — melainkan **teman refleksi yang aman** untuk siswa.

### Goals

| #   | Tujuan                           | Deskripsi                                                                      |
| --- | -------------------------------- | ------------------------------------------------------------------------------ |
| 1   | **Menamai emosi**          | Membantu siswa menamai emosi dengan tepat menggunakan Feeling Wheel (Plutchik) |
| 2   | **Refleksi ringan & aman** | Guided self-reflection melalui 5 pertanyaan reflektif (MHCM-based)             |
| 3   | **Respon natural & empatik** | Bot memberikan narasi reflektif yang manusiawi menggunakan Gemini            |

### Scope & Batasan

| ✅ Dalam Scope                        | ❌ Di Luar Scope              |
| ------------------------------------- | ----------------------------- |
| Pendamping refleksi emosi             | Diagnosis klinis              |
| Guided self-reflection (5 pertanyaan) | Terapi / konseling            |
| Emotion naming (Feeling Wheel)        | Pengambil keputusan           |
| Narasi reflektif (MHCM)               | Pengganti profesional         |
| Tips coping ringan                    | Assessment formal             |
| Respon natural dari Gemini            | Label klinis / scoring klinis |

### 🟢 Zona Kesejahteraan (Non-Klinis)

| Zona                       | Indikator                              | Aksi Chatbot                          |
| -------------------------- | -------------------------------------- | ------------------------------------- |
| 🟢 **Seimbang**            | Emosi stabil, mampu mengelola perasaan | Validasi + tips ringan                |
| 🟡 **Beradaptasi**         | Ada tekanan tapi masih coping          | Refleksi mendalam + coping strategies |
| 🟠 **Butuh Dukungan**      | Emosi intens berulang, sulit coping    | Tips coping + saran cari dukungan     |
| 🔴 **Perlu Perhatian**     | Indikasi intens/berulang               | Tips grounding + saran bicara orang terdekat |

### Expected Outcomes (MVP)

| Outcome                        | Deskripsi                                                    |
| ------------------------------ | ------------------------------------------------------------ |
| **Peningkatan literasi emosi** | Siswa mampu menamai emosi dengan tepat                       |
| **Refleksi yang membantu**     | Siswa mendapat narasi reflektif yang manusiawi & validatif   |
| **Tips actionable**            | Siswa mendapat coping tips praktis sesuai emosinya           |

### Keputusan Arsitektur

| Keputusan                    | Alasan                                                                                 |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| **Hanya Gemini API**         | Cukup pintar untuk deteksi emosi + generate narasi reflektif                           |
| **Multi-Turn 4 Fase**        | User bercerita → 5 refleksi → narasi MHCM → pilihan lanjutan. Bukan 1-shot Q&A         |
| **Pertanyaan dari JSON**     | 5 self-reflection questions dari knowledge base per emosi, tidak di-generate tiap kali |
| **Gemini hanya 2x per sesi** | Call #1: deteksi emosi (awal). Call #2: generate narasi reflektif (setelah 5 jawaban)  |
| **Tanpa RAG/Embedding**      | Knowledge base di-inject langsung ke prompt sebagai JSON                               |
| **Tanpa Redis**              | Session state cukup dari PostgreSQL                                                    |
| **Safe Framing**             | Selalu buka dengan "Aku di sini untuk bantu refleksi, bukan mendiagnosis"              |

### 🎡 Plutchik's Wheel of Emotion (Feeling Wheel)

Model emosi 3 tingkat yang dipakai Gemini untuk **menamai & memetakan emosi** pengguna:

| Level        | Emosi                                                                                      | Deskripsi                |
| ------------ | ------------------------------------------------------------------------------------------ | ------------------------ |
| **Primer**   | Joy, Trust, Fear, Surprise, Sadness, Disgust, Anger, Anticipation                          | 8 emosi dasar            |
| **Sekunder** | Love, Submission, Awe, Disapproval, Remorse, Contempt, Aggressiveness, Optimism            | Kombinasi 2 emosi primer |
| **Tersier**  | Serenity, Acceptance, Apprehension, Distraction, Pensiveness, Boredom, Annoyance, Interest | Intensitas/nuansa emosi  |

### Cara Kerja — 4 Fase Percakapan

| Fase | Nama                 | Apa yang Terjadi                                                                  | Gemini?    |
| ---- | -------------------- | --------------------------------------------------------------------------------- | ---------- |
| 1    | **BERCERITA**        | User curhat/cerita → Gemini deteksi emosi → Bot buka safe framing + validasi      | 🔷 Call #1 |
| 2    | **REFLEKSI RINGAN**  | Bot tanya 5 pertanyaan reflektif (dari JSON per emosi) → User jawab satu per satu | ⚡ No LLM  |
| 3    | **NARASI REFLEKTIF** | Setelah 5 jawaban → Gemini generate narasi MHCM + zona kesejahteraan              | 🔷 Call #2 |
| 4    | **TIPS & CLOSING**   | Bot kasih tips coping ringan + closing message yang empatik                       | ⚡ No LLM  |

```
Fase 1 — BERCERITA:
  User: "Aku merasa tidak bisa fokus belajar, rasanya semua menumpuk..."
  → 🔷 Gemini Call #1: Deteksi emosi (sadness + fear)
  → Bot: "Aku di sini untuk bantu refleksi, bukan mendiagnosis.
          Terima kasih sudah berbagi. Sepertinya ada perasaan berat
          yang kamu rasakan. Boleh aku tanya beberapa hal?"

Fase 2 — REFLEKSI RINGAN (5 pertanyaan dari JSON, tanpa Gemini):
  Bot: Q1 "Kapan terakhir kali kamu merasa seperti ini?"
  User: jawab → Bot: Q2 "Apa yang biasanya kamu lakukan saat merasa seperti ini?"
  User: jawab → Bot: Q3 "Siapa yang biasanya kamu ajak cerita?"
  User: jawab → Bot: Q4 "Bagaimana perasaan ini mempengaruhi aktivitasmu?"
  User: jawab → Bot: Q5 "Apa yang kamu harapkan berubah dari situasi ini?"
  User: jawab →

Fase 3 — NARASI REFLEKTIF:
  → 🔷 Gemini Call #2: Generate narasi + zona MHCM
  → Bot: "Dalam beberapa waktu terakhir, perasaan yang muncul cukup
          beragam dan terasa intens, terutama setelah kejadian yang
          menuntut banyak energi. Ada kesan bahwa tubuh dan pikiranmu
          sedang bekerja keras untuk beradaptasi."
  → Zona: 🟡 Beradaptasi

Fase 4 — TIPS & CLOSING:
  Bot: "Berikut beberapa tips yang mungkin bisa membantu:
  1. Grounding 5-4-3-2-1 (5 hal yang kamu lihat, 4 yang kamu dengar...)
  2. Jeda sejenak dan tarik napas dalam
  3. Tulis 3 hal yang kamu syukuri hari ini
  
  Terima kasih sudah berbagi. Kamu selalu bisa kembali kapan saja."
```

> **Total: 2 panggilan Gemini per SESI percakapan (bukan per message).** 5 pertanyaan refleksi diambil dari JSON knowledge base tanpa Gemini call.

---

## ✨ Fitur Utama

| #   | Fitur                                 | Deskripsi                                                                                                                               | Fase   |
| --- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 1   | 🎡 **Emotion Naming Assistant**       | Guided Feeling Wheel exploration — membantu user menamai emosi dengan tepat menggunakan Plutchik's Wheel via Gemini                     | Fase 1 |
| 2   | 💬 **Reflective Questions**           | 5 pertanyaan terbuka & empatik dari JSON knowledge base per emosi — untuk memvalidasi dan mengeksplorasi perasaan user (tanpa Gemini)   | Fase 2 |
| 3   | 📝 **Narrative Reflection Generator** | Gemini merangkum emosi dengan bahasa manusiawi tanpa label klinis — "Dalam beberapa waktu terakhir..." bukan "Kamu mengalami kecemasan" | Fase 3 |
| 4   | 📊 **Wellness Zone Mapping**          | Mapping emosi ke zona kesejahteraan (Seimbang/Beradaptasi/Butuh Dukungan/Perlu Perhatian)                                               | Fase 3 |
| 5   | 💡 **Coping Tips**                    | Tips ringan (grounding, jeda, journaling) berdasarkan emosi yang terdeteksi                                                             | Fase 4 |

### 🛡️ Safety & Boundary Layer

| Trigger                                  | Aksi Chatbot                                                                 |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| User minta diagnosis                     | Penolakan halus: "Aku tidak bisa mendiagnosis, tapi aku bisa bantu refleksi" |
| Indikasi intens/berulang                 | Tips grounding + saran bicara orang terdekat atau profesional                |
| User minta saran medis                   | Redirect ke profesional: "Untuk hal ini, sebaiknya konsultasi ke..."         |
| Pertanyaan di luar scope (akademik, dll) | Batasan sopan: "Aku fokus membantu refleksi emosi, untuk hal lain..."        |

---

## 🔄 Alur Sistem — 4 Fase Percakapan

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     EDUMIND AI — 4 FASE PERCAKAPAN                               │
│                    (Total: 2 Gemini call per SESI)                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   USER       │
│  "Aku merasa │
│   tidak bisa │
│   fokus..."  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FASE 1: BERCERITA                                           🔷 GEMINI CALL #1  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐   │
│  │   INPUT USER       │────▶│   GEMINI API       │────▶│   OUTPUT           │   │
│  │   (Cerita/Curhat)  │     │   Deteksi Emosi    │     │   • Emosi detected │   │
│  │                    │     │   via Feeling Wheel│     │   • Safe framing   │   │
│  └────────────────────┘     └────────────────────┘     │   • Validasi awal  │   │
│                                                         └────────────────────┘   │
│                                                                                  │
│  Bot: "Aku di sini untuk bantu refleksi, bukan mendiagnosis.                    │
│        Terima kasih sudah berbagi. Sepertinya ada perasaan berat..."            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FASE 2: REFLEKSI RINGAN                                     ⚡ NO GEMINI CALL  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    5 PERTANYAAN DARI JSON KNOWLEDGE BASE                  │   │
│  │                    (Per emosi yang terdeteksi di Fase 1)                  │   │
│  ├──────────────────────────────────────────────────────────────────────────┤   │
│  │  Q1: "Kapan terakhir kali kamu merasa seperti ini?"           → User jawab│   │
│  │  Q2: "Apa yang biasanya kamu lakukan saat merasa seperti ini?"→ User jawab│   │
│  │  Q3: "Siapa yang biasanya kamu ajak cerita?"                  → User jawab│   │
│  │  Q4: "Bagaimana perasaan ini mempengaruhi aktivitasmu?"       → User jawab│   │
│  │  Q5: "Apa yang kamu harapkan berubah dari situasi ini?"       → User jawab│   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  💡 Pertanyaan diambil dari: data/knowledge_base/reflection_questions.json      │
│  💡 Tidak ada Gemini call — pertanyaan sudah pre-defined per emosi              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FASE 3: NARASI REFLEKTIF (MHCM)                             🔷 GEMINI CALL #2  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐   │
│  │   INPUT            │────▶│   GEMINI API       │────▶│   OUTPUT           │   │
│  │   • Cerita awal    │     │   Generate Narasi  │     │   • Narasi MHCM    │   │
│  │   • 5 jawaban user │     │   Reflektif        │     │   • Zona wellness  │   │
│  │   • Emosi detected │     │                    │     │   • Insight        │   │
│  └────────────────────┘     └────────────────────┘     └────────────────────┘   │
│                                                                                  │
│  ✅ NARASI YANG BENAR (tanpa label klinis):                                     │
│  "Dalam beberapa waktu terakhir, perasaan yang muncul cukup beragam dan         │
│   terasa intens, terutama setelah kejadian yang menuntut banyak energi.         │
│   Ada kesan bahwa tubuh dan pikiranmu sedang bekerja keras untuk beradaptasi."  │
│                                                                                  │
│  ❌ NARASI YANG SALAH (dengan label klinis):                                    │
│  "Kamu mengalami kecemasan tingkat tinggi dan berisiko stres."                  │
│                                                                                  │
│  📊 Zona Wellness: 🟡 Beradaptasi                                               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FASE 4: TIPS & CLOSING                                      ⚡ NO GEMINI CALL  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐          │
│  │   TIPS COPING RINGAN (dari JSON knowledge base)                               │          │
│  │                                                                               │          │
│  │   • Grounding 5-4-3-2-1 (5 hal yang kamu lihat, 4 yang kamu dengar...)       │          │
│  │   • Teknik jeda sejenak + tarik napas dalam                                  │          │
│  │   • Journaling prompt (tulis 3 hal yang kamu syukuri)                        │          │
│  │   • Latihan pernapasan kotak (4-4-4-4)                                       │          │
│  └─────────────────────────────────────────────────────────────────────────┘          │
│                                                                                  │
│  💡 Tips diambil dari: data/knowledge_base/coping_tips.json                     │
│  💡 Closing message: "Terima kasih sudah berbagi. Kamu selalu bisa kembali."   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Ringkasan Penggunaan Gemini API (MVP)

| Fase | Nama             | Gemini Call? | Deskripsi                             |
| ---- | ---------------- | ------------ | ------------------------------------- |
| 1    | BERCERITA        | 🔷 Call #1   | Deteksi emosi + safe framing          |
| 2    | REFLEKSI RINGAN  | ⚡ Tidak     | 5 pertanyaan dari JSON knowledge base |
| 3    | NARASI REFLEKTIF | 🔷 Call #2   | Generate narasi MHCM + zona wellness  |
| 4    | TIPS & CLOSING   | ⚡ Tidak     | Tips coping ringan + closing message  |

> **Total: 2 panggilan Gemini per SESI** — bukan per message. Ini menghemat biaya API dan memastikan konsistensi.

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│            EDUMIND AI - SYSTEM ARCHITECTURE (Simplified)                         │
│                         4-Fase Multi-Turn Conversation                          │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │     CLIENT      │
                              │  (Mobile/Web)   │
                              └────────┬────────┘
                                       │
                                       │ HTTPS/REST
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   FastAPI    │  │    Rate      │  │    Auth      │  │   Error      │        │
│  │   Router     │  │   Limiter    │  │  Middleware  │  │   Handler    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SERVICE LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                      CONVERSATION ORCHESTRATOR                           │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌────────────┐ │    │
│  │  │  Phase       │  │  Emotion     │  │  Reflection  │  │  Narrative   │ │    │
│  │  │  Manager     │  │  Service     │  │  Service     │  │  Service     │ │    │
│  │  │  (4 Fase)    │  │  (Gemini)    │  │  (JSON KB)   │  │  (MHCM)      │ │    │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                          SUPPORT SERVICES (MVP)                          │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                 │    │
│  │  │  Session     │  │  Coping      │  │  Safety      │                 │    │
│  │  │  Manager     │  │  Tips        │  │  Layer       │                 │    │
│  │  │              │  │  (JSON)      │  │              │                 │    │
│  │  └───────────────┘  └───────────────┘  └───────────────┘                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CORE LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────┐      ┌──────────────────────────┐                 │
│  │       LLM MODULE         │      │   KNOWLEDGE BASE        │                 │
│  │  ┌──────────────────┐   │      │  ┌──────────────────┐    │                 │
│  │  │  Gemini Client   │   │      │  │ Reflection Q's   │    │                 │
│  │  ├──────────────────┤   │      │  │ (5 per emosi)    │    │                 │
│  │  │  Prompt Manager  │   │      │  ├──────────────────┤    │                 │
│  │  ├──────────────────┤   │      │  │ Coping Tips      │    │                 │
│  │  │  Emotion Prompt  │   │      │  ├──────────────────┤    │                 │
│  │  ├──────────────────┤   │      │  │ Feeling Wheel    │    │                 │
│  │  │  Narrative Prompt│   │      │  ├──────────────────┤    │                 │
│  │  └──────────────────┘   │      │  │ Wellness Zones   │    │                 │
│  └──────────────────────────┘      │  └──────────────────┘    │                 │
│                                   └──────────────────────────┘                 │
│                                                                                  │
│  ┌──────────────────────────┐      ┌──────────────────────────┐                 │
│  │    VALIDATION MODULE    │      │      EMOTION MODULE      │                 │
│  │  ┌──────────────────┐   │      │  ┌──────────────────┐    │                 │
│  │  │  Safety Checker  │   │      │  │  Wheel of Emotion│    │                 │
│  │  ├──────────────────┤   │      │  ├──────────────────┤    │                 │
│  │  │  Boundary Filter │   │      │  │  Zone Mapper     │    │                 │
│  │  ├──────────────────┤   │      │  ├──────────────────┤    │                 │
│  │  │  Input Validator │   │      │  │  Trend Analyzer  │    │                 │
│  │  └──────────────────┘   │      │  └──────────────────┘    │                 │
│  └──────────────────────────┘      └──────────────────────────┘                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES (Simplified)                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│            ┌────────────────────┐          ┌────────────────────┐            │
│            │   GOOGLE GEMINI   │          │   POSTGRESQL       │            │
│            │   API             │          │   (Database)       │            │
│            │                    │          │   + SQLAlchemy     │            │
│            │   • Emotion Detect │          │                    │            │
│            │   • Narrative Gen  │          │   • Sessions        │            │
│            │                    │          │   • Messages        │            │
│            │   (2 calls/session)│          │   • Emotion Logs    │            │
│            └────────────────────┘          │   • Reflections     │            │
│                                              └────────────────────┘            │
│                                                                                  │
│  ❌ DIHAPUS: ChromaDB, Redis, LangChain, FAISS, Sentence-Transformers           │
│  ✅ DISEDERHANAKAN: Knowledge Base langsung di-inject sebagai JSON               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Keputusan Arsitektur

| Komponen Dihapus         | Alasan                                                |
| ------------------------ | ----------------------------------------------------- |
| ❌ ChromaDB / FAISS      | Knowledge base cukup kecil, inject langsung ke prompt |
| ❌ Sentence-Transformers | Tidak perlu embedding, JSON langsung dibaca           |
| ❌ LangChain             | Over-engineering untuk 2 Gemini calls per sesi        |
| ❌ Redis                 | Session state cukup dari PostgreSQL                   |

| Komponen Dipertahankan     | Alasan                                                  |
| -------------------------- | ------------------------------------------------------- |
| ✅ Google Gemini API       | Cukup pintar untuk deteksi emosi + generate narasi      |
| ✅ PostgreSQL + SQLAlchemy | Menyimpan sessions, messages, emotion logs, reflections |
| ✅ FastAPI                 | REST API dengan async support                           |
| ✅ Pydantic v2             | Validasi request/response                               |

---

## 📁 Struktur Project

```
edumind-ai-service/
│
├── 📁 app/
│   ├── 📄 __init__.py                 # Inisialisasi aplikasi
│   ├── 📄 main.py                     # Entry point FastAPI
│   └── 📄 config.py                   # Pengaturan konfigurasi
│
├── 📁 database/
│   ├── 📄 __init__.py
│   ├── 📄 connection.py               # PostgreSQL connection & session management
│   ├── 📄 base.py                     # Base model untuk SQLAlchemy
│   │
│   ├── 📁 models/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py                 # Model User (siswa)
│   │   ├── 📄 session.py              # Model Chat Session (4 fase state)
│   │   ├── 📄 message.py              # Model Chat Message
│   │   ├── 📄 emotion_log.py          # Model log deteksi emosi
│   │   └── 📄 reflection.py           # Model refleksi (5 Q&A + narasi MHCM)
│   │
│   ├── 📁 repositories/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_repository.py      # Generic CRUD repository
│   │   ├── 📄 user_repository.py      # User data access
│   │   ├── 📄 session_repository.py   # Session data access (fase state)
│   │   └── 📄 reflection_repository.py # Reflection data access
│   │
│   └── 📁 migrations/
│       ├── 📄 env.py                  # Alembic environment config
│       ├── 📄 script.py.mako          # Migration template
│       └── 📁 versions/
│           └── 📄 001_initial.py      # Initial migration
│
├── 📁 core/
│   ├── 📄 __init__.py
│   │
│   ├── 📁 llm/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 gemini_client.py        # Wrapper Gemini API (2 calls/session)
│   │   └── 📄 prompts.py              # Template prompt (emotion + narrative)
│   │
│   ├── 📁 knowledge/                  # ✅ Langsung JSON, tanpa RAG
│   │   ├── 📄 __init__.py
│   │   ├── 📄 loader.py               # Load JSON knowledge base
│   │   └── 📄 question_selector.py    # Pilih 5 pertanyaan per emosi
│   │
│   └── 📁 conversation/               # ✅ 4-Fase State Machine
│       ├── 📄 __init__.py
│       ├── 📄 phase_manager.py        # State machine (BERCERITA→REFLEKSI→NARASI→LANJUTAN)
│       ├── 📄 phase_handlers.py       # Handler per fase
│       └── 📄 session_context.py      # Session context (emosi, jawaban, zona)
│
├── 📁 modules/
│   ├── 📄 __init__.py
│   │
│   ├── 📁 emotion/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 wheel_of_emotion.py     # Plutchik's Wheel (primer, sekunder, tersier)
│   │   ├── 📄 detector.py             # Deteksi emosi via Gemini (Fase 1)
│   │   ├── 📄 zone_mapper.py          # Mapping ke zona kesejahteraan
│   │   └── 📄 trend_analyzer.py       # Analisis trend emosi periodik
│   │
│   ├── 📁 reflection/                 # ✅ 5 Pertanyaan + Narasi MHCM
│   │   ├── 📄 __init__.py
│   │   ├── 📄 question_service.py     # Ambil 5 pertanyaan dari JSON (Fase 2)
│   │   └── 📄 narrative_generator.py  # Generate narasi MHCM via Gemini (Fase 3)
│   │
│   ├── 📁 safety/                     # ✅ Safety & Boundary Layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 boundary_checker.py     # Cek batasan (no diagnosis, no therapy)
│   │   └── 📄 safe_framing.py         # Safe framing responses
│   │
│   └── 📁 tips/                       # ✅ Coping Tips (Fase 4)
│       ├── 📄 __init__.py
│       └── 📄 tips_service.py         # Load & serve tips dari JSON
│
├── 📁 services/
│   ├── 📄 __init__.py
│   ├── 📄 conversation_service.py     # ✅ Orchestrator 4 Fase
│   ├── 📄 emotion_service.py          # Layanan deteksi emosi
│   └── 📄 reflection_service.py       # Layanan refleksi (5 Q + narasi)
│
├── 📁 api/
│   ├── 📄 __init__.py
│   │
│   ├── 📁 endpoints/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 conversation.py         # ✅ Multi-turn conversation (4 fase)
│   │   └── 📄 health.py               # Health check
│   │
│   ├── 📄 router.py                   # Router API utama
│   │
│   ├── 📁 schemas/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 conversation_schema.py  # Request/response multi-turn
│   │   ├── 📄 reflection_schema.py    # Schema refleksi + narasi MHCM
│   │   └── 📄 common_schema.py        # Model umum
│   │
│   └── 📁 middleware/
│       ├── 📄 __init__.py
│       ├── 📄 rate_limiter.py         # Pembatasan rate
│       └── 📄 error_handler.py        # Penanganan error global
│
├── 📁 data/
│   └── 📁 knowledge_base/             # ✅ JSON files (tanpa RAG/embedding)
│       ├── 📄 wheel_of_emotion.json       # Plutchik's Wheel (3 level)
│       ├── 📄 reflection_questions.json   # ✅ 5 pertanyaan per emosi
│       ├── 📄 coping_tips.json            # Tips grounding, jeda, journaling
│       └── 📄 wellness_zones.json         # Definisi 4 zona kesejahteraan
│
├── 📁 tests/
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py                 # Konfigurasi pengujian
│   │
│   ├── 📁 unit/
│   │   ├── 📄 test_phase_manager.py       # Test 4-fase state machine
│   │   ├── 📄 test_emotion_detector.py    # Test deteksi emosi
│   │   └── 📄 test_narrative_generator.py # Test narasi MHCM
│   │
│   └── 📁 integration/
│       ├── 📄 test_conversation_flow.py   # Test 4-fase flow end-to-end
│       └── 📄 test_api_endpoints.py       # Test endpoint API
│
├── 📁 scripts/
│   ├── 📄 seed_knowledge_base.py      # Seed JSON knowledge base
│   └── 📄 test_gemini_connection.py   # Test koneksi Gemini API
│
├── 📁 docs/
│   ├── 📄 API.md                      # Dokumentasi API
│   ├── 📄 ARCHITECTURE.md             # Detail arsitektur
│   └── 📄 SETUP.md                    # Panduan setup
│
├── 📄 .env.example                    # Template variabel environment
├── 📄 .gitignore
├── 📄 requirements.txt                # Dependensi Python
├── 📄 pyproject.toml                  # Konfigurasi project
├── 📄 alembic.ini                     # Konfigurasi Alembic
├── 📄 Dockerfile                      # Konfigurasi Docker
├── 📄 docker-compose.yml              # Docker compose
└── 📄 README.md                       # Dokumentasi project
```

---

## 🔧 Tech Stack

| Komponen           | Teknologi          | Fungsi                                                |
| ------------------ | ------------------ | ----------------------------------------------------- |
| **Framework API**  | FastAPI            | REST API dengan async support                         |
| **LLM**            | Google Gemini      | Deteksi emosi (Call #1) + Narasi reflektif (Call #2)  |
| **Database**       | PostgreSQL         | Sessions, messages, reflections, emotion logs         |
| **ORM**            | SQLAlchemy (async) | Object-Relational Mapping                             |
| **Validasi**       | Pydantic v2        | Request/response validation                           |
| **Migrasi DB**     | Alembic            | Database migration management                         |
| **Knowledge Base** | JSON files         | 5 pertanyaan per emosi, coping tips, wellness zones   |
| **Pengujian**      | Pytest             | Unit & integration test                                     |
| **Kontainerisasi** | Docker             | Deployment                                                  |

### ❌ Komponen Dihapus (Simplified)

| Komponen              | Alasan Dihapus                                        |
| --------------------- | ----------------------------------------------------- |
| LangChain             | Over-engineering untuk 2 Gemini calls per sesi        |
| ChromaDB / FAISS      | Knowledge base cukup kecil, inject langsung ke prompt |
| Sentence-Transformers | Tidak perlu embedding, JSON langsung dibaca           |
| Redis                 | Session state cukup dari PostgreSQL                   |

---

## 📦 Dependensi

### Framework Inti

```txt
fastapi==0.109.0                # Framework web
uvicorn[standard]==0.27.0       # Server ASGI
pydantic==2.5.3                 # Validasi data
pydantic-settings==2.1.0        # Manajemen pengaturan
python-dotenv==1.0.0            # Variabel environment
```

### Database & ORM (PostgreSQL + SQLAlchemy)

```txt
psycopg2-binary==2.9.9          # PostgreSQL adapter untuk Python
asyncpg==0.29.0                 # Async PostgreSQL driver
sqlalchemy==2.0.25              # ORM untuk Python
sqlalchemy[asyncio]==2.0.25     # Async support untuk SQLAlchemy
alembic==1.13.1                 # Database migration tool
greenlet==3.0.3                 # Required untuk SQLAlchemy async
```

### LLM (Google Gemini Only)

```txt
google-generativeai==0.3.2      # API Google Gemini (hanya ini!)
```

> **Catatan:** Tidak menggunakan LangChain. Gemini API dipanggil langsung untuk:
>
> - **Call #1:** Deteksi emosi (Fase 1)
> - **Call #2:** Generate narasi reflektif MHCM (Fase 3)

### ❌ Dependensi Dihapus

| Paket                    | Alasan Dihapus                                 |
| ------------------------ | ---------------------------------------------- |
| `langchain`              | Over-engineering untuk 2 Gemini calls per sesi |
| `langchain-google-genai` | Cukup pakai `google-generativeai` langsung     |
| `chromadb`               | Knowledge base kecil, inject JSON ke prompt    |
| `faiss-cpu`              | Tidak perlu vector search                      |
| `sentence-transformers`  | Tidak perlu embedding                          |
| `redis`                  | Session state cukup dari PostgreSQL            |

### Pemrosesan Data

```txt
aiofiles==23.2.1                # Operasi file async (load JSON KB)
```

### Utilitas

```txt
httpx==0.26.0                   # HTTP client
tenacity==8.2.3                 # Logika retry untuk Gemini API
structlog==24.1.0               # Logging terstruktur
python-json-logger==2.0.7       # Logging JSON
```

### Keamanan

```txt
python-jose[cryptography]==3.3.0  # Penanganan JWT
passlib[bcrypt]==1.7.4            # Hashing password
```

### Pengujian

```txt
pytest==7.4.4                   # Framework pengujian
pytest-asyncio==0.23.3          # Pengujian async
pytest-cov==4.1.0               # Coverage
```

### Development

```txt
black==24.1.1                   # Pemformatan kode
isort==5.13.2                   # Pengurutan import
flake8==7.0.0                   # Linting
mypy==1.8.0                     # Type checking
pre-commit==3.6.0               # Pre-commit hooks
```

---

## 🚀 Instalasi

### Prasyarat

- Python 3.10+
- PostgreSQL 14+ (database utama)
- Akun Google Cloud dengan akses Gemini API

### Langkah-Langkah Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/edumind-ai-service.git
cd edumind-ai-service

# 2. Buat virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Setup variabel environment
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# 5. Edit file .env dan tambahkan API keys + Database config

# 6. Setup PostgreSQL Database
psql -U postgres -c "CREATE DATABASE edumind_db;"

# 7. Jalankan migrasi database
alembic upgrade head

# 8. Seed knowledge base (JSON files)
python scripts/seed_knowledge_base.py

# 9. Jalankan aplikasi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 10. Jalankan pengujian
pytest tests/ -v
```

### Setup Docker

```bash
# Build image
docker build -t edumind-ai-service .

# Jalankan dengan docker-compose (termasuk PostgreSQL)
docker-compose up -d
```

### Docker Compose (docker-compose.yml)

```yaml
version: "3.8"

services:
  app:
    build: .
    container_name: edumind-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/edumind_db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./data:/app/data
    networks:
      - edumind-network

  db:
    image: postgres:15-alpine
    container_name: edumind-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: edumind_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - edumind-network

# ❌ DIHAPUS: Redis service (tidak diperlukan)

volumes:
  postgres_data:

networks:
  edumind-network:
    driver: bridge
```

---

## ⚙️ Konfigurasi

### Variabel Environment (.env)

```env
# Aplikasi
APP_NAME=EduMindAI
APP_ENV=development
DEBUG=true

# API Google Gemini
GEMINI_API_KEY=masukkan_api_key_gemini_anda
GEMINI_MODEL=gemini-pro

# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=edumind_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Knowledge Base Path
KNOWLEDGE_BASE_PATH=./data/knowledge_base

# Keamanan
SECRET_KEY=masukkan_secret_key_anda
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ❌ DIHAPUS: Vector Store, Embedding Model, Redis

# Pembatasan Rate
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Timeout Configuration
GEMINI_TIMEOUT_SECONDS=30
GEMINI_RETRY_ATTEMPTS=3
SESSION_TIMEOUT_MINUTES=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "https://edumind.sekolah.id"]
CORS_ALLOW_CREDENTIALS=true

# Language/i18n
DEFAULT_LANGUAGE=id
SUPPORTED_LANGUAGES=["id", "en"]

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 🌐 Language Support (i18n)

**EduMindAI** mendukung **Bahasa Indonesia** sebagai bahasa utama, dengan dukungan **English** sebagai fallback.

```
┌────────────────────────────────────────────────────────────────────┐
│                   LANGUAGE DETECTION FLOW                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  1. User Input → Gemini auto-detect bahasa                         │
│  2. Response mengikuti bahasa input user                           │
│  3. Knowledge Base tersedia dalam ID & EN                          │
│  4. Fallback ke Bahasa Indonesia jika tidak terdeteksi             │
│                                                                    │
│  Header: Accept-Language: id-ID atau en-US                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

| Komponen | Bahasa Indonesia | English |
|----------|------------------|----------|
| **Emotion Labels** | ✅ Sedih, Marah, Cemas | ✅ Sad, Angry, Anxious |
| **Reflection Questions** | ✅ 5 pertanyaan per emosi | ✅ 5 questions per emotion |
| **Coping Tips** | ✅ Tips grounding, journaling | ✅ Grounding, journaling tips |
| **Narrative MHCM** | ✅ Generated by Gemini | ✅ Generated by Gemini |
| **UI Messages** | ✅ Safe framing ID | ✅ Safe framing EN |

**Knowledge Base Bilingual:**

```json
// reflection_questions.json
{
  "sedih": {
    "id": [
      "Kapan terakhir kamu merasa seperti ini?",
      "Apa yang biasanya membantumu saat merasa sedih?"
    ],
    "en": [
      "When was the last time you felt like this?",
      "What usually helps you when you feel sad?"
    ]
  }
}
```

### 🔢 API Versioning

```
✅ Current: /api/v1/conversation/start
✅ Future:  /api/v2/conversation/start (when breaking changes)

Header: X-API-Version: 1.0.0
```

| Version | Status | Breaking Changes |
|---------|--------|------------------|
| `v1` | ✅ Active | - |
| `v2` | 🔜 Planned | Multi-session support |

---

## 🔌 API Endpoints (MVP)

### Endpoint Conversation (4-Fase Multi-Turn)

| Method   | Endpoint                               | Fase   | Deskripsi                                     |
| -------- | -------------------------------------- | ------ | --------------------------------------------- |
| `POST`   | `/api/conversation/start`              | Fase 1 | User bercerita → Gemini deteksi emosi         |
| `POST`   | `/api/conversation/reflect`            | Fase 2 | Kirim jawaban refleksi (1 dari 5 pertanyaan)  |
| `GET`    | `/api/conversation/narrative`          | Fase 3 | Get narasi MHCM setelah 5 jawaban             |
| `POST`   | `/api/conversation/tips`               | Fase 4 | Get tips coping ringan + closing message      |
| `GET`    | `/api/conversation/{session_id}/state` | -      | Get current session state (fase, emosi, zona) |
| `DELETE` | `/api/conversation/{session_id}`       | -      | Hapus session                                 |

### Endpoint Health

| Method | Endpoint            | Deskripsi            |
| ------ | ------------------- | -------------------- |
| `GET`  | `/api/health`       | Cek kesehatan sistem |
| `GET`  | `/api/health/ready` | Cek kesiapan sistem  |

### Contoh Flow — 4 Fase Lengkap

#### Fase 1: BERCERITA (🔷 Gemini Call #1)

```bash
# Request
curl -X POST "http://localhost:8000/api/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "siswa-123",
    "message": "Aku merasa tidak bisa fokus belajar, rasanya semua menumpuk..."
  }'
```

```json
// Response
{
  "session_id": "sess-abc-123",
  "phase": "BERCERITA",
  "emotion_detected": {
    "primary": "sadness",
    "secondary": "fear",
    "zone": "BERADAPTASI"
  },
  "bot_message": "Aku di sini untuk bantu refleksi, bukan mendiagnosis. Terima kasih sudah berbagi. Sepertinya ada perasaan berat yang kamu rasakan. Boleh aku tanya beberapa hal?",
  "next_action": "REFLECTION_Q1"
}
```

#### Fase 2: REFLEKSI RINGAN (⚡ No Gemini — 5 Pertanyaan dari JSON)

```bash
# Request Q1
curl -X POST "http://localhost:8000/api/conversation/reflect" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc-123",
    "question_index": 1,
    "answer": "Sudah sekitar 2 minggu terakhir"
  }'
```

```json
// Response
{
  "session_id": "sess-abc-123",
  "phase": "REFLEKSI_RINGAN",
  "current_question": 1,
  "total_questions": 5,
  "next_question": "Apa yang biasanya kamu lakukan saat merasa seperti ini?",
  "next_action": "REFLECTION_Q2"
}
```

#### Fase 3: NARASI REFLEKTIF (🔷 Gemini Call #2)

```bash
# Request — setelah 5 jawaban selesai
curl -X GET "http://localhost:8000/api/conversation/narrative?session_id=sess-abc-123"
```

```json
// Response
{
  "session_id": "sess-abc-123",
  "phase": "NARASI_REFLEKTIF",
  "narrative": "Dalam beberapa waktu terakhir, perasaan yang muncul cukup beragam dan terasa intens, terutama setelah kejadian yang menuntut banyak energi. Ada kesan bahwa tubuh dan pikiranmu sedang bekerja keras untuk beradaptasi.",
  "wellness_zone": {
    "zone": "BERADAPTASI",
    "emoji": "🟡",
    "description": "Ada tekanan tapi masih bisa coping"
  },
  "next_action": "TIPS_CLOSING"
}
```

#### Fase 4: TIPS & CLOSING (⚡ No Gemini)

```bash
# Request — get tips dan closing message
curl -X POST "http://localhost:8000/api/conversation/tips" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc-123"
  }'
```

```json
// Response
{
  "session_id": "sess-abc-123",
  "phase": "SELESAI",
  "tips": [
    {
      "name": "Grounding 5-4-3-2-1",
      "description": "5 hal yang kamu lihat, 4 yang kamu dengar..."
    },
    {
      "name": "Jeda Sejenak",
      "description": "Istirahat 5 menit, tarik napas dalam..."
    },
    {
      "name": "Journaling",
      "description": "Tulis 3 hal yang kamu syukuri hari ini..."
    }
  ],
  "closing_message": "Terima kasih sudah berbagi. Kamu selalu bisa kembali kapan saja."
}
```

---

## 📝 Detail Module (MVP)

### 1. Modul Emotion (`modules/emotion/`)

**Fungsi:** Deteksi emosi menggunakan Plutchik's Wheel via Gemini API (Fase 1).

| File                  | Deskripsi                                        |
| --------------------- | ------------------------------------------------ |
| `wheel_of_emotion.py` | Plutchik's Wheel (primer, sekunder, tersier)     |
| `detector.py`         | Deteksi emosi via Gemini API (🔷 Call #1)        |
| `zone_mapper.py`      | Mapping emosi ke Zona Kesejahteraan (4 zona)     |
| `trend_analyzer.py`   | Analisis trend emosi periodik (mingguan/bulanan) |

#### Plutchik's Wheel of Emotion - Detail

**Emosi Primer (8 Emosi Dasar):**

| Emosi        | Deskripsi    | Intensitas Tinggi | Intensitas Rendah |
| ------------ | ------------ | ----------------- | ----------------- |
| Joy          | Kegembiraan  | Ecstasy           | Serenity          |
| Trust        | Kepercayaan  | Admiration        | Acceptance        |
| Fear         | Ketakutan    | Terror            | Apprehension      |
| Surprise     | Keterkejutan | Amazement         | Distraction       |
| Sadness      | Kesedihan    | Grief             | Pensiveness       |
| Disgust      | Rasa jijik   | Loathing          | Boredom           |
| Anger        | Kemarahan    | Rage              | Annoyance         |
| Anticipation | Antisipasi   | Vigilance         | Interest          |

**Emosi Sekunder (Kombinasi):**

| Emosi          | Kombinasi Dari       |
| -------------- | -------------------- |
| Love           | Joy + Trust          |
| Submission     | Trust + Fear         |
| Awe            | Fear + Surprise      |
| Disapproval    | Surprise + Sadness   |
| Remorse        | Sadness + Disgust    |
| Contempt       | Disgust + Anger      |
| Aggressiveness | Anger + Anticipation |
| Optimism       | Anticipation + Joy   |

### 2. Modul Reflection (`modules/reflection/`)

**Fungsi:** 5 pertanyaan reflektif dari JSON + generate narasi MHCM (Fase 2 & 3).

| File                     | Deskripsi                                       |
| ------------------------ | ----------------------------------------------- |
| `question_service.py`    | Ambil 5 pertanyaan dari JSON per emosi (Fase 2) |
| `narrative_generator.py` | Generate narasi MHCM via Gemini (🔷 Call #2)    |

### 3. Modul Safety (`modules/safety/`)

**Fungsi:** Safety & Boundary Layer — penolakan halus, safe framing.

| File                  | Deskripsi                                     |
| --------------------- | --------------------------------------------- |
| `boundary_checker.py` | Cek batasan (no diagnosis, no therapy advice) |
| `safe_framing.py`     | Response templates dengan safe framing        |

### 4. Modul Tips (`modules/tips/`)

**Fungsi:** Coping tips ringan untuk Fase 4.

| File              | Deskripsi                            |
| ----------------- | ------------------------------------ |
| `tips_service.py` | Load & serve tips dari JSON per emosi |

### 5. Core LLM (`core/llm/`)

**Fungsi:** Wrapper Gemini API — hanya 2 calls per session.

| File               | Deskripsi                                         |
| ------------------ | ------------------------------------------------- |
| `gemini_client.py` | Wrapper Gemini API dengan retry & error handling  |
| `prompts.py`       | Prompt templates (emotion detect + narrative gen) |

### 6. Core Conversation (`core/conversation/`)

**Fungsi:** 4-Fase State Machine untuk multi-turn conversation.

| File                 | Deskripsi                                              |
| -------------------- | ------------------------------------------------------ |
| `phase_manager.py`   | State machine (BERCERITA→REFLEKSI→NARASI→LANJUTAN)     |
| `phase_handlers.py`  | Handler logic per fase                                 |
| `session_context.py` | Session context (emosi, jawaban refleksi, zona, state) |

### 7. Core Knowledge (`core/knowledge/`)

**Fungsi:** Load JSON knowledge base tanpa embedding/RAG.

| File                   | Deskripsi                                   |
| ---------------------- | ------------------------------------------- |
| `loader.py`            | Load JSON files dari `data/knowledge_base/` |
| `question_selector.py` | Pilih 5 pertanyaan refleksi per emosi       |

---

## 📊 Alur Chat Detail — Multi-Turn 4 Fase

### State Machine Overview (MVP)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SESSION STATE MACHINE — 4 FASE (MVP)                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │  BERCERITA  │───▶│  REFLEKSI   │───▶│   NARASI    │───▶│   TIPS &    │     │
│   │   (Fase 1)  │    │  (Fase 2)   │    │  (Fase 3)   │    │  CLOSING    │     │
│   │  🔷 Gemini  │    │  ⚡ No LLM  │    │  🔷 Gemini  │    │  ⚡ No LLM  │     │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘     │
│          │                  │                  │                  │             │
│          ▼                  ▼                  ▼                  ▼             │
│   User bercerita      5 pertanyaan      Generate          Tips coping        │
│   → Deteksi emosi      dari JSON →      narasi MHCM      + closing           │
│   → Safe framing      User jawab       + zona wellness   message              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Session Context (Tersimpan di PostgreSQL)

```python
class SessionContext:
    session_id: str
    user_id: str
    current_phase: PhaseEnum  # BERCERITA, REFLEKSI, NARASI, TIPS_CLOSING, SELESAI

    # Fase 1 results
    initial_story: str
    detected_emotion: EmotionResult
    wellness_zone_initial: WellnessZone

    # Fase 2 progress
    reflection_questions: List[str]     # 5 pertanyaan dari JSON
    reflection_answers: List[str]       # 5 jawaban user
    current_question_index: int         # 0-4

    # Fase 3 results
    mhcm_narrative: str                 # Narasi reflektif dari Gemini
    wellness_zone_final: WellnessZone   # Zona setelah refleksi

    # Fase 4 results
    tips_shown: List[str]               # Tips yang ditampilkan

    # Metadata
    created_at: datetime
    updated_at: datetime
    gemini_call_count: int              # Max: 2 per session
```

### Phase Transitions

| Dari         | Ke           | Trigger                         | Gemini Call? |
| ------------ | ------------ | ------------------------------- | ------------ |
| START        | BERCERITA    | `POST /conversation/start`      | 🔷 Call #1   |
| BERCERITA    | REFLEKSI     | Emotion detected                | ⚡ No        |
| REFLEKSI     | REFLEKSI     | `POST /conversation/reflect` x5 | ⚡ No        |
| REFLEKSI     | NARASI       | 5 jawaban lengkap               | 🔷 Call #2   |
| NARASI       | TIPS_CLOSING | Narrative generated             | ⚡ No        |
| TIPS_CLOSING | SELESAI      | `POST /conversation/tips`       | ⚡ No        |

---

## 🏆 API Design Best Practices (MVP)

### 1. Multi-Turn Conversation Flow

```
✅ Stateful session management via PostgreSQL
✅ Phase-based endpoints (/start, /reflect, /narrative, /tips)
✅ Max 2 Gemini calls per session (cost optimization)
✅ Knowledge base dari JSON (tanpa RAG/embedding)
```

### 2. Response Structure Standar

```json
{
  "success": true,
  "data": {
    "session_id": "sess-abc-123",
    "phase": "REFLEKSI_RINGAN",
    "current_question": 2,
    ...
  },
  "metadata": {
    "request_id": "uuid-v4",
    "timestamp": "2026-02-08T10:30:00Z",
    "gemini_calls_remaining": 1
  }
}
```

### 3. Error Handling

| HTTP Code | Error Code              | Kondisi                     |
| --------- | ----------------------- | --------------------------- |
| 400       | `VALIDATION_ERROR`      | Input tidak valid           |
| 400       | `PHASE_MISMATCH`        | Wrong phase for operation   |
| 404       | `SESSION_NOT_FOUND`     | Session tidak ditemukan     |
| 429       | `GEMINI_LIMIT_EXCEEDED` | Sudah 2 calls dalam session |
| 500       | `INTERNAL_ERROR`        | Error server                |

### 4. API Documentation

```
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
OpenAPI JSON: http://localhost:8000/openapi.json
```

---

### 5. Alur Detail per Fase

#### FASE 1: BERCERITA (🔷 Gemini Call #1)

```http
POST /api/conversation/start HTTP/1.1
Content-Type: application/json

{
  "student_id": "siswa-001",
  "message": "Aku merasa sedih karena dimarahi ortu"
}
```

**Response:**

```json
{
  "session_id": "sess-uuid-123",
  "current_phase": "BERCERITA",
  "emotion_detected": {
    "primary": "sadness",
    "primary_id": "Sedih",
    "validated": true,
    "safe_frame": "Aku di sini untuk bantu refleksi, bukan mendiagnosis."
  },
  "next_action": "PROCEED_TO_REFLECT",
  "message": "Terima kasih sudah berbagi. Aku dengar kamu merasa 'Sedih'. Aku di sini untuk bantu refleksi, bukan mendiagnosis. Klik lanjut untuk refleksi ringan."
}
```

#### FASE 2: REFLEKSI RINGAN (⚡ No Gemini Call)

```http
POST /api/conversation/reflect HTTP/1.1
Content-Type: application/json

{
  "session_id": "sess-uuid-123"
}
```

**Response (Satu pertanyaan per request, total 5 pertanyaan):**

```json
{
  "session_id": "sess-uuid-123",
  "current_phase": "REFLEKSI_RINGAN",
  "question_number": 1,
  "total_questions": 5,
  "question": "Kapan terakhir kamu merasa seperti ini?",
  "source": "reflection_questions.json",
  "next_action": "ANSWER_OR_SKIP"
}
```

**Submit Jawaban:**

```http
POST /api/conversation/reflect/answer HTTP/1.1
Content-Type: application/json

{
  "session_id": "sess-uuid-123",
  "question_number": 1,
  "answer": "Kemarin malam saat dapat nilai jelek"
}
```

#### FASE 3: NARASI REFLEKTIF (🔷 Gemini Call #2)

```http
POST /api/conversation/narrative HTTP/1.1
Content-Type: application/json

{
  "session_id": "sess-uuid-123"
}
```

**Response:**

```json
{
  "session_id": "sess-uuid-123",
  "current_phase": "NARASI_REFLEKTIF",
  "narrative": {
    "summary": "Dari yang kamu ceritakan, sepertinya kamu sedang dalam proses memahami perasaanmu tentang situasi dengan orang tua. Wajar jika kamu merasa sedih — itu menunjukkan bahwa hubungan ini penting buatmu.",
    "wellness_zone": "BERADAPTASI",
    "wellness_label": "🟡 Zona Beradaptasi",
    "mhcm_compliant": true
  },
  "coping_tips": [
    "Cobalah journaling 5 menit sebelum tidur",
    "Berbagi cerita dengan teman yang dipercaya"
  ],
  "next_action": "PROCEED_TO_CHOICE"
}
```

#### FASE 4: TIPS & CLOSING (⚡ No Gemini Call)

```http
POST /api/conversation/tips HTTP/1.1
Content-Type: application/json

{
  "session_id": "sess-uuid-123"
}
```

**Response:**

```json
{
  "session_id": "sess-uuid-123",
  "current_phase": "SELESAI",
  "tips": [
    {"name": "Grounding 5-4-3-2-1", "description": "5 hal yang kamu lihat, 4 yang kamu dengar..."},
    {"name": "Jeda Sejenak", "description": "Istirahat 5 menit, tarik napas dalam..."},
    {"name": "Journaling", "description": "Tulis 3 hal yang kamu syukuri hari ini..."}
  ],
  "closing_message": "Terima kasih sudah berbagi. Kamu selalu bisa kembali kapan saja."
}
```

---

### 6. Error Responses

| HTTP Code | Error Code                | Kondisi                       |
| --------- | ------------------------- | ----------------------------- |
| 400       | `VALIDATION_ERROR`        | Input tidak valid             |
| 400       | `PHASE_MISMATCH`          | Wrong phase for this endpoint |
| 404       | `SESSION_NOT_FOUND`       | Session tidak ditemukan       |
| 429       | `GEMINI_LIMIT_EXCEEDED`   | Sudah 2 Gemini calls session  |
| 500       | `INTERNAL_ERROR`          | Error server                  |
| 503       | `GEMINI_UNAVAILABLE`      | Gemini API tidak tersedia     |

**Error Response Format:**

```json
{
  "success": false,
  "error": {
    "code": "PHASE_MISMATCH",
    "message": "Cannot call /reflect before completing BERCERITA phase",
    "current_phase": "BERCERITA",
    "expected_phase": "REFLEKSI_RINGAN"
  },
  "session_id": "sess-uuid-123"
}
```

---

### 7. API Design Best Practices

#### Phase-Aware Endpoints

```
✅ Endpoints per fase (bukan single endpoint)
   /api/conversation/start     → Fase 1
   /api/conversation/reflect   → Fase 2
   /api/conversation/narrative → Fase 3
   /api/conversation/choice    → Fase 4

✅ Session-based state management
   Setiap request membawa session_id
   Server tracks current_phase per session

✅ Gemini call optimization
   Hanya 2 calls per session (Fase 1 & 3)
   Fase 2 & 4 menggunakan JSON knowledge base
```

#### Response Structure Standar

```json
{
  "success": true,
  "session_id": "sess-uuid-123",
  "current_phase": "BERCERITA",
  "data": { ... },
  "next_action": "PROCEED_TO_REFLECT",
  "metadata": {
    "timestamp": "2026-02-02T10:30:00Z",
    "gemini_calls_used": 1,
    "gemini_calls_remaining": 1
  }
}
```

#### Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-Request-ID: uuid-v4 (auto-generated per request)
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 8. CORS Configuration

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Processing-Time"]
)
```

### 9. Request ID Tracking

```python
# middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

### 10. Timeout & Retry Configuration

```python
# core/gemini.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class GeminiClient:
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)  # 30 seconds
        self.max_retries = 3
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(...)
        return response.json()
```

### 11. Graceful Shutdown

```python
# main.py
import signal
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting EduMindAI...")
    await database.connect()
    yield
    # Shutdown
    logger.info("Shutting down gracefully...")
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
```

---

## 📊 Monitoring & Observability

### Metrics (Prometheus)

```python
# middleware/metrics.py
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "edumind_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

GEMINI_LATENCY = Histogram(
    "edumind_gemini_latency_seconds",
    "Gemini API call duration",
    ["phase"]
)

SESSION_WELLNESS_ZONE = Counter(
    "edumind_wellness_zone_total",
    "Sessions by wellness zone",
    ["zone"]
)
```

### Metrics Dashboard (MVP)

| Metric | Deskripsi | Alert Threshold |
|--------|-----------|------------------|
| `edumind_gemini_latency_seconds` | Waktu respons Gemini | > 5 detik |
| `edumind_session_completion_rate` | % session selesai 4 fase | < 70% |
| `edumind_wellness_zone_total{zone="PERLU_PERHATIAN"}` | Jumlah zona 🔴 | > 10% dari total |
| `edumind_tips_served_total` | Total tips yang diberikan | monitoring |

### Structured Logging (JSON)

```json
{
  "timestamp": "2026-02-08T10:30:00Z",
  "level": "INFO",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "service": "conversation_service",
  "event": "phase_transition",
  "session_id": "sess-abc-123",
  "user_id": "siswa-001",
  "data": {
    "from_phase": "BERCERITA",
    "to_phase": "REFLEKSI_RINGAN",
    "detected_emotion": "sadness",
    "gemini_calls_used": 1,
    "duration_ms": 1250
  }
}
```

### Health Check Endpoints

```json
// GET /api/health
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "dependencies": {
    "database": "ok",
    "gemini_api": "ok"
  }
}

// GET /api/health/ready
{
  "ready": true,
  "database_connected": true,
  "gemini_quota_remaining": 95
}
```

---

## 🗄️ Database Schema (PostgreSQL + SQLAlchemy) — MVP

### Entity Relationship Diagram (ERD) — 4 Fase Model

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     DATABASE SCHEMA — 4 FASE MODEL (MVP)                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐    │
│  │     USERS       │       │      SESSIONS       │       │    MESSAGES     │    │
│  ├─────────────────┤       ├─────────────────────┤       ├─────────────────┤    │
│  │ id (PK)         │──┐    │ id (PK)             │──┐    │ id (PK)         │    │
│  │ student_id      │  │    │ user_id (FK)        │  │    │ session_id (FK) │    │
│  │ name            │  └───►│ current_phase       │  └───►│ role            │    │
│  │ class           │       │ detected_emotion    │       │ content         │    │
│  │ created_at      │       │ wellness_zone       │       │ created_at      │    │
│  │ updated_at      │       │ gemini_calls_used   │       └─────────────────┘    │
│  └─────────────────┘       │ started_at          │              │               │
│                            │ ended_at            │              │               │
│                            │ is_active           │              ▼               │
│                            └─────────────────────┘    ┌─────────────────┐       │
│                                    │                  │   REFLECTIONS   │       │
│                                    │                  ├─────────────────┤       │
│                                    │                  │ id (PK)         │       │
│                                    │                  │ session_id (FK) │       │
│                                    │                  │ question_number │       │
│                                    ├─────────────────►│ question_text   │       │
│                                    │                  │ answer_text     │       │
│                                    │                  │ created_at      │       │
│                                    │                  └─────────────────┘       │
│                                    │                                            │
│                                    ▼                                            │
│                             ┌─────────────────┐                                 │
│                             │   NARRATIVES    │                                 │
│                             ├─────────────────┤                                 │
│                             │ id (PK)         │                                 │
│                             │ session_id (FK) │                                 │
│                             │ summary_text    │                                 │
│                             │ wellness_zone   │                                 │
│                             │ coping_tips     │ (JSON)                          │
│                             │ mhcm_compliant  │                                 │
│                             │ created_at      │                                 │
│                             └─────────────────┘                                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

PHASE VALUES: BERCERITA | REFLEKSI_RINGAN | NARASI_REFLEKTIF | TIPS_CLOSING | SELESAI
WELLNESS ZONES: SEIMBANG | BERADAPTASI | BUTUH_DUKUNGAN | PERLU_PERHATIAN
```

### Model SQLAlchemy (Updated for 4-Phase MVP)

#### database/base.py

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Async engine untuk PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class untuk semua model
Base = declarative_base()

# Dependency untuk FastAPI
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

#### database/models/user.py

```python
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
```

#### database/models/session.py (Updated for 4-Phase MVP)

```python
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 4-Phase State Management (MVP)
    current_phase = Column(String(30), default="BERCERITA")  # BERCERITA, REFLEKSI_RINGAN, NARASI_REFLEKTIF, TIPS_CLOSING, SELESAI
    detected_emotion = Column(String(50), nullable=True)     # Primary emotion from Fase 1
    wellness_zone = Column(String(30), nullable=True)        # From Fase 3 narrative
    gemini_calls_used = Column(Integer, default=0)           # Max 2 per session
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="session", cascade="all, delete-orphan")
    narrative = relationship("Narrative", back_populates="session", uselist=False)
```

#### database/models/reflection.py (NEW — Fase 2)

```python
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database.base import Base

class Reflection(Base):
    """Stores 5 reflection Q&A from Fase 2 (REFLEKSI RINGAN)"""
    __tablename__ = "reflections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)  # 1-5
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)  # Nullable if skipped
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="reflections")
```

#### database/models/narrative.py (NEW — Fase 3)

```python
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from database.base import Base

class Narrative(Base):
    """Stores MHCM-compliant narrative from Fase 3 (NARASI REFLEKTIF)"""
    __tablename__ = "narratives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), unique=True, nullable=False)
    summary_text = Column(Text, nullable=False)  # MHCM narrative
    wellness_zone = Column(String(30), nullable=False)  # SEIMBANG, BERADAPTASI, etc.
    coping_tips = Column(JSONB, default=[])  # List of tips from JSON
    mhcm_compliant = Column(Boolean, default=True)  # Validation flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="narrative")
```

#### database/models/message.py

```python
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20))  # 'user' atau 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token_count = Column(Integer, default=0)

    # Relationships
    session = relationship("Session", back_populates="messages")
```

### Repository Pattern

#### database/repositories/base_repository.py

```python
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, id, **kwargs) -> Optional[ModelType]:
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        return await self.get_by_id(id)

    async def delete(self, id) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0
```

### Alembic Migration

#### database/migrations/versions/001_initial.py

```python
"""Initial migration"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None

def upgrade():
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('external_id', sa.String(255), unique=True, nullable=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Sessions table
    op.create_table('sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('metadata', postgresql.JSON, default={})
    )

    # Messages table
    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sessions.id')),
        sa.Column('role', sa.String(20)),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('token_count', sa.Integer, default=0)
    )

    # Emotion logs table
    op.create_table('emotion_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id')),
        sa.Column('primary_emotion', sa.String(50)),
        sa.Column('secondary_emotion', sa.String(50)),
        sa.Column('tertiary_emotion', sa.String(50)),
        sa.Column('confidence', sa.Float),
        sa.Column('urgency_level', sa.String(20)),
        sa.Column('sentiment_score', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Feedbacks table
    op.create_table('feedbacks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id')),
        sa.Column('rating', sa.Integer),
        sa.Column('comment', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_messages_session_id', 'messages', ['session_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

def downgrade():
    op.drop_table('feedbacks')
    op.drop_table('emotion_logs')
    op.drop_table('messages')
    op.drop_table('sessions')
    op.drop_table('users')
```

---

## 📋 Struktur Knowledge Base — JSON Files

### reflection_questions.json (Fase 2)

```json
{
  "description": "5 pertanyaan refleksi per emosi untuk Fase 2 REFLEKSI RINGAN",
  "emotions": {
    "sedih": {
      "emotion_id": "sadness",
      "emotion_label": "Sedih",
      "questions": [
        "Kapan terakhir kamu merasa seperti ini?",
        "Apa yang biasanya membantumu saat merasa sedih?",
        "Siapa orang yang biasanya mendukungmu?",
        "Hal kecil apa yang bisa membuatmu sedikit lebih baik hari ini?",
        "Bagaimana perasaanmu mempengaruhi aktivitas harianmu?"
      ]
    },
    "marah": {
      "emotion_id": "anger",
      "emotion_label": "Marah",
      "questions": [
        "Apa yang memicu perasaan marah ini?",
        "Bagaimana kamu biasanya mengekspresikan kemarahan?",
        "Apakah ada pola yang kamu sadari dengan perasaan ini?",
        "Apa yang kamu butuhkan saat ini untuk merasa lebih tenang?",
        "Siapa yang bisa kamu ajak bicara tentang ini?"
      ]
    },
    "cemas": {
      "emotion_id": "fear",
      "emotion_label": "Cemas",
      "questions": [
        "Apa yang paling membuatmu khawatir saat ini?",
        "Bagaimana kecemasan ini mempengaruhi tidurmu?",
        "Apa strategi yang pernah membantumu mengatasi kecemasan?",
        "Hal apa yang bisa kamu kontrol dalam situasi ini?",
        "Bagaimana perasaanmu setelah berbagi cerita ini?"
      ]
    },
    "senang": {
      "emotion_id": "joy",
      "emotion_label": "Senang",
      "questions": [
        "Apa yang membuatmu merasa senang hari ini?",
        "Bagaimana kamu bisa mempertahankan perasaan positif ini?",
        "Siapa yang ingin kamu ajak berbagi kebahagiaan ini?",
        "Apa yang kamu pelajari dari pengalaman positif ini?",
        "Bagaimana perasaan ini mempengaruhi hubunganmu dengan orang lain?"
      ]
    },
    "bingung": {
      "emotion_id": "surprise",
      "emotion_label": "Bingung",
      "questions": [
        "Apa yang membuatmu merasa bingung?",
        "Informasi apa yang kamu butuhkan untuk lebih jelas?",
        "Siapa yang bisa membantumu memahami situasi ini?",
        "Langkah kecil apa yang bisa kamu ambil sekarang?",
        "Bagaimana perasaanmu tentang ketidakpastian ini?"
      ]
    },
    "kecewa": {
      "emotion_id": "disgust",
      "emotion_label": "Kecewa",
      "questions": [
        "Apa yang membuatmu merasa kecewa?",
        "Harapan apa yang tidak terpenuhi?",
        "Bagaimana kamu biasanya mengatasi kekecewaan?",
        "Apa yang bisa kamu lakukan berbeda ke depannya?",
        "Siapa yang bisa membantumu melewati ini?"
      ]
    }
  }
}
```

### wellness_zones.json (Fase 3 — MVP)

```json
{
  "description": "Zona kesejahteraan untuk kategorisasi non-klinis (MVP)",
  "zones": [
    {
      "id": "SEIMBANG",
      "label": "🟢 Zona Seimbang",
      "description": "Kondisi emosional stabil, mampu mengelola perasaan dengan baik",
      "indicators": ["Mampu mengenali emosi", "Punya strategi coping", "Dukungan sosial baik"],
      "coping_priority": "maintenance"
    },
    {
      "id": "BERADAPTASI",
      "label": "🟡 Zona Beradaptasi",
      "description": "Sedang dalam proses penyesuaian, perlu dukungan ringan",
      "indicators": ["Emosi fluktuatif", "Mencari strategi baru", "Butuh validasi"],
      "coping_priority": "exploration"
    },
    {
      "id": "BUTUH_DUKUNGAN",
      "label": "🟠 Zona Butuh Dukungan",
      "description": "Perlu dukungan lebih intensif dari orang terdekat",
      "indicators": ["Kesulitan mengelola emosi", "Dampak pada aktivitas harian", "Butuh support"],
      "coping_priority": "intervention"
    },
    {
      "id": "PERLU_PERHATIAN",
      "label": "🔴 Zona Perlu Perhatian",
      "description": "Disarankan untuk berbicara dengan orang terdekat atau profesional",
      "indicators": ["Distress signifikan", "Perlu perhatian ekstra", "Butuh dukungan intensif"],
      "coping_priority": "urgent"
    }
  ]
}
```

### coping_tips.json (Fase 4)

```json
{
  "description": "Tips coping per emosi untuk narrative response",
  "tips_by_emotion": {
    "sadness": [
      "Cobalah journaling 5 menit sebelum tidur untuk menuangkan perasaan",
      "Berbagi cerita dengan teman atau keluarga yang dipercaya",
      "Melakukan aktivitas fisik ringan seperti jalan kaki 10 menit",
      "Mendengarkan musik yang menenangkan",
      "Menulis 3 hal yang kamu syukuri hari ini"
    ],
    "anger": [
      "Tarik napas dalam 4-7-8 (tarik 4 detik, tahan 7 detik, hembuskan 8 detik)",
      "Berikan jeda 10 detik sebelum merespons situasi",
      "Tulis perasaanmu di kertas lalu robek dan buang",
      "Lakukan aktivitas fisik untuk melepaskan energi",
      "Coba teknik grounding 5-4-3-2-1"
    ],
    "fear": [
      "Teknik grounding: identifikasi 5 hal yang bisa dilihat, 4 yang disentuh, 3 yang didengar",
      "Fokus pada hal yang bisa kamu kontrol saat ini",
      "Bicara dengan orang dewasa yang dipercaya tentang kekhawatiranmu",
      "Tulis skenario terburuk dan terrealistis",
      "Praktikkan pernapasan kotak (4-4-4-4)"
    ],
    "joy": [
      "Catat momen bahagia ini di jurnal",
      "Bagikan kebahagiaan dengan orang terdekat",
      "Buat rencana untuk mengulang pengalaman positif",
      "Ekspresikan rasa syukur kepada orang yang berkontribusi",
      "Simpan foto atau kenangan dari momen ini"
    ]
  }
}
```

### feeling_wheel.json (Literasi Emosi)

```json
{
  "description": "Plutchik's Feeling Wheel untuk literasi emosi - mapping ke Bahasa Indonesia",
  "wheel": {
    "primary_emotions": [
      {"en": "joy", "id": "Senang", "color": "#FFD700"},
      {"en": "trust", "id": "Percaya", "color": "#98FB98"},
      {"en": "fear", "id": "Cemas", "color": "#228B22"},
      {"en": "surprise", "id": "Bingung", "color": "#00CED1"},
      {"en": "sadness", "id": "Sedih", "color": "#4169E1"},
      {"en": "disgust", "id": "Kecewa", "color": "#9932CC"},
      {"en": "anger", "id": "Marah", "color": "#DC143C"},
      {"en": "anticipation", "id": "Harap", "color": "#FF8C00"}
    ]
  },
  "safe_framing_phrase": "Aku di sini untuk bantu refleksi, bukan mendiagnosis."
}
```

---

## ✅ Checklist Implementasi — MVP (4 Fase Model)

### Core Setup

- [ ] Setup struktur project (folder structure sesuai dokumentasi)
- [ ] Konfigurasi environment dan dependencies (requirements.txt)
- [ ] Setup FastAPI dengan routers modular
- [ ] Konfigurasi logging dan error handling

### Database (PostgreSQL + SQLAlchemy)

- [ ] Setup PostgreSQL database
- [ ] Konfigurasi SQLAlchemy async connection
- [ ] Buat model User (student_id, name, class)
- [ ] Buat model Session (dengan current_phase, detected_emotion, wellness_zone, gemini_calls_used)
- [ ] Buat model Message
- [ ] Buat model Reflection (5 Q&A per session)
- [ ] Buat model Narrative (MHCM summary, wellness zone, coping tips)
- [ ] Setup Alembic untuk migrasi
- [ ] Buat initial migration
- [ ] Implementasi repository pattern

### Fase 1: BERCERITA (Gemini Call #1)

- [ ] Implementasi PhaseManager service
- [ ] Implementasi EmotionDetectionService via Gemini
- [ ] Mapping Plutchik's Wheel ke Bahasa Indonesia
- [ ] Validasi emosi dengan safe framing phrase
- [ ] Endpoint `POST /api/conversation/start`
- [ ] Unit test emotion detection

### Fase 2: REFLEKSI RINGAN (No Gemini)

- [ ] Implementasi ReflectionService
- [ ] Load questions dari reflection_questions.json
- [ ] Serve 5 pertanyaan sequentially per emosi
- [ ] Handle skip/answer untuk tiap pertanyaan
- [ ] Endpoint `POST /api/conversation/reflect`
- [ ] Endpoint `POST /api/conversation/reflect/answer`
- [ ] Unit test reflection flow

### Fase 3: NARASI REFLEKTIF (Gemini Call #2)

- [ ] Implementasi NarrativeService via Gemini
- [ ] Build prompt dengan reflection answers sebagai context
- [ ] Generate MHCM-compliant narrative (no clinical labels)
- [ ] Assign wellness zone dari narrative
- [ ] Attach coping tips dari coping_tips.json
- [ ] Endpoint `POST /api/conversation/narrative`
- [ ] MHCM compliance validation
- [ ] Unit test narrative generation

### Fase 4: TIPS & CLOSING (No Gemini)

- [ ] Implementasi TipsService
- [ ] Load tips dari coping_tips.json per emosi
- [ ] Generate closing message
- [ ] Endpoint `POST /api/conversation/tips`
- [ ] Unit test tips flow

### Safety Layer

- [ ] Implementasi SafetyService
- [ ] Boundary checking (no diagnosis, no therapy)
- [ ] Safe framing messages
- [ ] Rate limiting (max 2 Gemini calls per session)
- [ ] Input sanitization

### Knowledge Base (JSON Files)

- [ ] Buat reflection_questions.json (5 pertanyaan per emosi)
- [ ] Buat wellness_zones.json (4 zona dengan indikator)
- [ ] Buat coping_tips.json (tips per emosi)
- [ ] Buat feeling_wheel.json (Plutchik mapping ID)
- [ ] Unit test JSON loading

### Testing

- [ ] Unit test per module
- [ ] Integration test 4-phase flow (end-to-end)
- [ ] Test Gemini call limit enforcement
- [ ] Test wellness zone assignment
- [ ] Test natural response quality

### Deployment

- [ ] Konfigurasi Docker & docker-compose
- [ ] Setup PostgreSQL container
- [ ] Environment variables (.env.example)
- [ ] API documentation (Swagger/ReDoc)
- [ ] Health check endpoint

### Industry Standards

- [ ] Implementasi i18n/Language Support (ID/EN)
- [ ] Setup Accept-Language header handling
- [ ] Buat bilingual knowledge base (ID/EN)
- [ ] Implementasi API versioning (/api/v1/, /api/v2/)
- [ ] Setup CORS middleware
- [ ] Implementasi Request ID tracking (X-Request-ID)
- [ ] Konfigurasi Timeout & Retry (tenacity)
- [ ] Implementasi Graceful Shutdown (lifespan)
- [ ] Setup Prometheus metrics (/metrics)
- [ ] Konfigurasi Structured Logging (JSON format)
- [ ] Enhanced Health Check endpoints (/health, /health/ready, /health/live)

---

## 📄 Lisensi

MIT License - lihat [LICENSE](LICENSE) untuk detail.

---

## 👥 Kontributor

- Tim Development PT Kreasi Bali Sasmita

---

## 📞 Dukungan

Untuk pertanyaan atau issue, silakan buat GitHub Issue atau hubungi tim development.
