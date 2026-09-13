-- File: 001_initial_schema.sql
-- Deskripsi: Membuat tabel inti, constraint, index, trigger, dan view Football Analyst PWA.
-- Dibuat: 2026-09-14
-- Versi: v1.0.0

-- RESET MANUAL (jalankan hanya jika ingin menghapus seluruh skema):
-- DROP VIEW IF EXISTS view_accuracy_stats CASCADE;
-- DROP VIEW IF EXISTS view_daily_predictions CASCADE;
-- DROP TABLE IF EXISTS prediction_results CASCADE;
-- DROP TABLE IF EXISTS match_analyses CASCADE;
-- DROP TABLE IF EXISTS agent_runs CASCADE;
-- DROP TABLE IF EXISTS daily_matches CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS daily_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id TEXT UNIQUE NOT NULL,
  league TEXT NOT NULL,
  league_code TEXT,
  kickoff TIMESTAMPTZ NOT NULL,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  home_team_id TEXT,
  away_team_id TEXT,
  match_score NUMERIC(5, 2) CHECK (match_score IS NULL OR (match_score >= 0 AND match_score <= 100)),
  agent_insight TEXT,
  model_version TEXT,
  is_published BOOLEAN NOT NULL DEFAULT TRUE,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS match_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES daily_matches(id) ON DELETE CASCADE,
  category TEXT NOT NULL CHECK (category IN ('over_under', 'btts', 'win', 'handicap')),
  pick TEXT NOT NULL,
  confidence NUMERIC(5, 2) CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 100)),
  odds NUMERIC(6, 2),
  extra JSONB NOT NULL DEFAULT '{}'::JSONB,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT match_analyses_match_category_unique UNIQUE (match_id, category)
);

CREATE TABLE IF NOT EXISTS prediction_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES match_analyses(id) ON DELETE CASCADE,
  actual_home_score INT,
  actual_away_score INT,
  actual_result TEXT,
  is_correct BOOLEAN,
  evaluated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_date DATE NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ,
  status TEXT CHECK (status IN ('running', 'success', 'failed')),
  matches_fetched INT NOT NULL DEFAULT 0,
  matches_selected INT NOT NULL DEFAULT 0,
  analyses_generated INT NOT NULL DEFAULT 0,
  error_message TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_daily_matches_kickoff
  ON daily_matches (kickoff DESC);

CREATE INDEX IF NOT EXISTS idx_daily_matches_league
  ON daily_matches (league);

CREATE INDEX IF NOT EXISTS idx_daily_matches_match_score
  ON daily_matches (match_score DESC);

CREATE INDEX IF NOT EXISTS idx_analyses_match
  ON match_analyses (match_id);

CREATE INDEX IF NOT EXISTS idx_analyses_category
  ON match_analyses (category);

CREATE INDEX IF NOT EXISTS idx_analyses_confidence
  ON match_analyses (confidence DESC);

CREATE INDEX IF NOT EXISTS idx_results_analysis
  ON prediction_results (analysis_id);

CREATE INDEX IF NOT EXISTS idx_results_is_correct
  ON prediction_results (is_correct);

CREATE INDEX IF NOT EXISTS idx_agent_runs_date
  ON agent_runs (run_date DESC);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trigger_daily_matches_updated_at ON daily_matches;
CREATE TRIGGER trigger_daily_matches_updated_at
BEFORE UPDATE ON daily_matches
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE VIEW view_daily_predictions
AS
SELECT
  dm.id AS daily_match_id,
  dm.match_id AS external_match_id,
  dm.league,
  dm.league_code,
  dm.kickoff,
  dm.home_team,
  dm.away_team,
  dm.match_score,
  dm.agent_insight,
  dm.model_version,
  ma.id AS analysis_id,
  ma.category,
  ma.pick,
  ma.confidence,
  ma.odds,
  ma.extra,
  ma.reason
FROM daily_matches AS dm
JOIN match_analyses AS ma ON ma.match_id = dm.id
WHERE dm.is_published = TRUE
ORDER BY dm.match_score DESC NULLS LAST, dm.kickoff ASC;

CREATE OR REPLACE VIEW view_accuracy_stats
AS
SELECT
  ma.category,
  COALESCE(pr.evaluated_at::DATE, pr.created_at::DATE) AS day,
  COUNT(*) AS evaluated_count,
  COUNT(*) FILTER (WHERE pr.is_correct IS TRUE) AS correct_count,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE pr.is_correct IS TRUE) / NULLIF(COUNT(*), 0),
    2
  ) AS accuracy_percent
FROM prediction_results AS pr
JOIN match_analyses AS ma ON ma.id = pr.analysis_id
JOIN daily_matches AS dm ON dm.id = ma.match_id
WHERE dm.is_published = TRUE
  AND pr.is_correct IS NOT NULL
GROUP BY ma.category, COALESCE(pr.evaluated_at::DATE, pr.created_at::DATE);
