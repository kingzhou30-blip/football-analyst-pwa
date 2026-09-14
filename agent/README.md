# Football Analyst Autonomous Agent

Agent FASE 5 adalah state machine linear berbasis Python. Implementasi tidak memakai LangGraph, LangChain, Pydantic, NumPy, atau library ML eksternal.

## Cara Menjalankan

```bash
cd agent
python run_daily.py
```

run_daily.py membaca environment dari ../backend/.env menggunakan python-dotenv. Variabel yang diperlukan adalah BZZOIRO_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, dan OPENROUTER_API_KEY.

Alur Enam Node

1. fetch_fixtures: mengambil fixtures hari ini dari Bzzoiro.
2. enrich_features: menambahkan xG, Elo, form, H2H, odds, confidence, dan value edge.
3. select_top: memilih maksimal tujuh pertandingan dengan selector ML.
4. analyze_matches: menjalankan Over/Under, BTTS, Win, dan Handicap.
5. generate_insight: membuat narasi dua kalimat melalui OpenRouter, dengan fallback lokal.
6. publish_to_supabase: menyimpan pertandingan dan empat analisisnya melalui REST API Supabase.

Setiap node menerima dan mengembalikan state: dict. Error dicatat ke state["errors"]; kegagalan fetch atau LLM tidak menghentikan pipeline. Jika Bzzoiro tidak mengembalikan data, pipeline melanjutkan dengan list kosong.

Output

Hasil akhir disimpan ke tabel daily_matches dan match_analyses di Supabase. Ringkasan jumlah fixture, pertandingan terpilih, analisis, publikasi, dan error dicetak ke terminal.
