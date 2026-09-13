-- File: 001_sample_data.sql
-- Deskripsi: Menyediakan dua pertandingan dan data analisis untuk pengujian frontend.
-- Dibuat: 2026-09-14
-- Versi: v1.0.0

-- Seed ini dapat dijalankan ulang untuk identifier pertandingan yang sama.

INSERT INTO daily_matches (
  match_id,
  league,
  league_code,
  kickoff,
  home_team,
  away_team,
  home_team_id,
  away_team_id,
  match_score,
  agent_insight,
  model_version,
  is_published
)
VALUES
(
  'sample-epl-man-city-liverpool-20260914',
  'Premier League',
  'EPL',
  '2026-09-14 19:00:00+00',
  'Manchester City',
  'Liverpool',
  'sample-home-man-city',
  'sample-away-liverpool',
  82.50,
  'Kedua tim memiliki produktivitas tinggi dan profil peluang yang mendukung pertandingan terbuka.',
  'v1.0.0',
  TRUE
),
(
  'sample-laliga-real-madrid-barcelona-20260914',
  'La Liga',
  'LL',
  '2026-09-14 21:00:00+00',
  'Real Madrid',
  'Barcelona',
  'sample-home-real-madrid',
  'sample-away-barcelona',
  79.00,
  'Kualitas serangan kedua tim dan riwayat pertemuan mengindikasikan peluang gol dari kedua sisi.',
  'v1.0.0',
  TRUE
)
ON CONFLICT (match_id) DO UPDATE SET
  match_score = EXCLUDED.match_score,
  agent_insight = EXCLUDED.agent_insight,
  model_version = EXCLUDED.model_version,
  is_published = EXCLUDED.is_published,
  updated_at = NOW();

WITH selected_matches AS (
  SELECT id, match_id
  FROM daily_matches
  WHERE match_id IN (
    'sample-epl-man-city-liverpool-20260914',
    'sample-laliga-real-madrid-barcelona-20260914'
  )
)
INSERT INTO match_analyses (match_id, category, pick, confidence, odds, extra, reason)
SELECT selected_matches.id, sample.category, sample.pick, sample.confidence, sample.odds, sample.extra, sample.reason
FROM selected_matches
JOIN (
  VALUES
    ('sample-epl-man-city-liverpool-20260914', 'over_under', 'Over 2.5', 74.00::NUMERIC, 1.72::NUMERIC, '{"home_xg": 1.85, "away_xg": 1.42}'::JSONB, 'Estimasi total gol dari distribusi Poisson berada di atas garis 2.5.'),
    ('sample-epl-man-city-liverpool-20260914', 'btts', 'BTTS Yes', 71.00::NUMERIC, 1.68::NUMERIC, '{"home_scored_rate": 0.88, "away_scored_rate": 0.81}'::JSONB, 'Kedua tim memiliki tingkat mencetak gol yang konsisten.'),
    ('sample-epl-man-city-liverpool-20260914', 'win', 'Home Win', 63.00::NUMERIC, 2.05::NUMERIC, '{"elo_edge": 0.62, "form_edge": 0.58, "h2h_edge": 0.55}'::JSONB, 'Keunggulan kandang dan rating gabungan memberi nilai pada tuan rumah.'),
    ('sample-epl-man-city-liverpool-20260914', 'handicap', 'Home -0.5', 61.00::NUMERIC, 1.90::NUMERIC, '{"xg_diff": 0.43, "line": -0.5}'::JSONB, 'Selisih xG positif mendukung handicap tipis untuk tuan rumah.'),
    ('sample-laliga-real-madrid-barcelona-20260914', 'over_under', 'Over 2.5', 72.00::NUMERIC, 1.80::NUMERIC, '{"home_xg": 1.68, "away_xg": 1.51}'::JSONB, 'Model Poisson memperkirakan total peluang gol yang tinggi.'),
    ('sample-laliga-real-madrid-barcelona-20260914', 'btts', 'BTTS Yes', 76.00::NUMERIC, 1.62::NUMERIC, '{"home_scored_rate": 0.86, "away_scored_rate": 0.84}'::JSONB, 'Profil serangan kedua tim mendukung gol dari kedua pihak.'),
    ('sample-laliga-real-madrid-barcelona-20260914', 'win', 'Home Win', 58.00::NUMERIC, 2.25::NUMERIC, '{"elo_edge": 0.56, "form_edge": 0.54, "h2h_edge": 0.52}'::JSONB, 'Keunggulan kandang tipis memberi pilihan pada tuan rumah.'),
    ('sample-laliga-real-madrid-barcelona-20260914', 'handicap', 'Home 0 (DNB)', 57.00::NUMERIC, 1.88::NUMERIC, '{"xg_diff": 0.17, "line": 0}'::JSONB, 'Selisih xG kecil sehingga garis draw no bet lebih konservatif.')
) AS sample(match_id_text, category, pick, confidence, odds, extra, reason)
  ON sample.match_id_text = selected_matches.match_id
ON CONFLICT (match_id, category) DO UPDATE SET
  pick = EXCLUDED.pick,
  confidence = EXCLUDED.confidence,
  odds = EXCLUDED.odds,
  extra = EXCLUDED.extra,
  reason = EXCLUDED.reason;

INSERT INTO agent_runs (
  run_date,
  started_at,
  finished_at,
  status,
  matches_fetched,
  matches_selected,
  analyses_generated,
  metadata
)
SELECT
  DATE '2026-09-14',
  '2026-09-14 05:00:00+00',
  '2026-09-14 05:04:30+00',
  'success',
  128,
  2,
  8,
  '{"source": "sample_seed", "environment": "testing"}'::JSONB
WHERE NOT EXISTS (
  SELECT 1
  FROM agent_runs
  WHERE run_date = DATE '2026-09-14'
    AND metadata->>'source' = 'sample_seed'
);

WITH selected_analyses AS (
  SELECT
    ma.id,
    dm.match_id AS external_match_id,
    ma.category
  FROM match_analyses AS ma
  JOIN daily_matches AS dm ON dm.id = ma.match_id
  WHERE dm.match_id IN (
    'sample-epl-man-city-liverpool-20260914',
    'sample-laliga-real-madrid-barcelona-20260914'
  )
  AND ma.category = 'over_under'
)
INSERT INTO prediction_results (
  analysis_id,
  actual_home_score,
  actual_away_score,
  actual_result,
  is_correct,
  evaluated_at
)
SELECT
  selected_analyses.id,
  CASE WHEN selected_analyses.external_match_id = 'sample-epl-man-city-liverpool-20260914' THEN 3 ELSE 2 END,
  CASE WHEN selected_analyses.external_match_id = 'sample-epl-man-city-liverpool-20260914' THEN 2 ELSE 2 END,
  'Over 2.5',
  TRUE,
  '2026-09-15 00:00:00+00'
FROM selected_analyses
WHERE NOT EXISTS (
  SELECT 1
FROM prediction_results AS pr
  WHERE pr.analysis_id = selected_analyses.id
);
