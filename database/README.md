Database Migration
Dokumen ini menjelaskan setup skema PostgreSQL untuk Football Analyst PWA di Supabase.
Urutan Eksekusi
Jalankan file berikut di Supabase Dashboard → SQL Editor dalam urutan ini:
migrations/001_initial_schema.sql
migrations/002_rls_policies.sql
seeds/001_sample_data.sql untuk data pengujian opsional
Jalankan setiap file secara terpisah agar error lebih mudah ditelusuri. Migration ditujukan untuk PostgreSQL 15+ dan objek utamanya dibuat secara idempotent.
Verifikasi
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'daily_matches',
    'match_analyses',
    'prediction_results',
    'agent_runs'
  )
ORDER BY table_name;

SELECT table_name, row_security
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN (
    'daily_matches',
    'match_analyses',
    'prediction_results',
    'agent_runs'
  )
ORDER BY tablename;

SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name IN ('view_daily_predictions', 'view_accuracy_stats')
ORDER BY table_name;

SELECT *
FROM view_daily_predictions
ORDER BY match_score DESC NULLS LAST, kickoff ASC;
Seed harus menghasilkan dua pertandingan, delapan analisis—empat untuk setiap pertandingan—satu agent_run berstatus success, dan dua prediction_results.
Rollback atau Reset
Migration tidak menjalankan DROP secara aktif. Untuk reset manual, tinjau bagian komentar RESET MANUAL di awal file migration, lalu jalankan perintah berikut hanya setelah memastikan dampaknya:
DROP VIEW IF EXISTS view_accuracy_stats CASCADE;
DROP VIEW IF EXISTS view_daily_predictions CASCADE;
DROP TABLE IF EXISTS prediction_results CASCADE;
DROP TABLE IF EXISTS match_analyses CASCADE;
DROP TABLE IF EXISTS agent_runs CASCADE;
DROP TABLE IF EXISTS daily_matches CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
Perintah reset menghapus data secara permanen. Jangan menjalankannya pada project produksi tanpa backup.
Row Level Security
RLS diaktifkan pada seluruh tabel. Role anon hanya dapat membaca daily_matches dengan is_published = TRUE, match_analyses yang terkait dengan pertandingan publik, serta prediction_results yang terkait dengan pertandingan publik. Role authenticated mendapatkan akses penuh sesuai policy admin. Role service_role mendapatkan akses penuh dan di Supabase biasanya juga melewati RLS secara default.
Jangan pernah mengekspos service role key di frontend, repository publik, atau browser. Simpan key hanya pada backend dan environment variable yang terlindungi.
Contoh Query Test
-- Pertandingan publik.
SELECT *
FROM daily_matches
WHERE is_published = TRUE
ORDER BY match_score DESC NULLS LAST, kickoff ASC;

-- Seluruh analisis yang dapat dibaca frontend.
SELECT *
FROM view_daily_predictions
ORDER BY match_score DESC NULLS LAST, kickoff ASC;

-- Akurasi per kategori dan hari.
SELECT *
FROM view_accuracy_stats
ORDER BY day DESC, category;

-- Jumlah analisis per pertandingan.
SELECT
  dm.home_team,
  dm.away_team,
  COUNT(ma.id) AS analysis_count
FROM daily_matches AS dm
LEFT JOIN match_analyses AS ma ON ma.match_id = dm.id
GROUP BY dm.id, dm.home_team, dm.away_team
ORDER BY dm.kickoff DESC;
Catatan Seed
001_sample_data.sql berisi contoh Manchester City vs Liverpool dan Real Madrid vs Barcelona, masing-masing dengan kategori over_under, btts, win, dan handicap. Data ini hanya untuk testing frontend dan bukan rekomendasi aktual.
