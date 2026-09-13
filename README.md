# ⚽ Football Analyst PWA

Progressive Web App untuk menyajikan analisis pertandingan sepak bola harian melalui pipeline data, machine learning, dan autonomous agent.

## 📊 Status

Proyek ini sedang berada pada **FASE 1: Setup struktur folder + file dasar**.

Implementasi backend, model ML, agent, frontend, deployment, dan integrasi layanan akan dilakukan pada fase berikutnya.

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Frontend | SvelteKit + Vite + TypeScript + vite-plugin-pwa |
| Backend | Python FastAPI + Uvicorn |
| Agent | LangGraph |
| ML | XGBoost + scipy (Poisson) + scikit-learn |
| Database | Supabase (PostgreSQL) |
| LLM | OpenRouter API (model gratis) |
| Data Bola | Bzzoiro Sports Data API |
| Hosting PWA | Cloudflare Pages |
| Hosting Backend | Render.com |
| Cron | GitHub Actions |

## 📁 Struktur Folder


## 🎯 Fitur

Setiap hari, agent akan menganalisis **5-7 pertandingan terbaik** dan menghasilkan 5 output:

1. **Over/Under** (Total Goals > 2.5)
2. **BTTS** (Both Teams To Score)
3. **Win** (Match Winner / 1X2)
4. **Handicap** (Asian Handicap)

## 🚀 Setup Lokal

*(Akan diisi pada fase berikutnya)*

## ☁️ Deployment

*(Akan diisi pada fase berikutnya)*

## ⚠️ Disclaimer

Rekomendasi yang dihasilkan bersifat **analitis dan informatif**. Tidak ada jaminan hasil pertandingan. Bertanggung jawablah dalam setiap keputusan.

## 📄 Lisensi

MIT
