-- File: 002_rls_policies.sql
-- Deskripsi: Mengaktifkan RLS dan menetapkan policy anon, authenticated, dan service_role.
-- Dibuat: 2026-09-14
-- Versi: v1.0.0

-- RESET MANUAL (jalankan hanya jika ingin menghapus policy):
-- DROP POLICY IF EXISTS daily_matches_public_read ON daily_matches;
-- DROP POLICY IF EXISTS match_analyses_public_read ON match_analyses;
-- DROP POLICY IF EXISTS prediction_results_public_read ON prediction_results;
-- DROP POLICY IF EXISTS daily_matches_authenticated_all ON daily_matches;
-- DROP POLICY IF EXISTS match_analyses_authenticated_all ON match_analyses;
-- DROP POLICY IF EXISTS prediction_results_authenticated_all ON prediction_results;
-- DROP POLICY IF EXISTS agent_runs_authenticated_all ON agent_runs;

ALTER TABLE daily_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS daily_matches_public_read ON daily_matches;
CREATE POLICY daily_matches_public_read
ON daily_matches
FOR SELECT
TO anon
USING (is_published = TRUE);

DROP POLICY IF EXISTS match_analyses_public_read ON match_analyses;
CREATE POLICY match_analyses_public_read
ON match_analyses
FOR SELECT
TO anon
USING (
  EXISTS (
    SELECT 1
    FROM daily_matches AS dm
    WHERE dm.id = match_analyses.match_id
      AND dm.is_published = TRUE
  )
);

DROP POLICY IF EXISTS prediction_results_public_read ON prediction_results;
CREATE POLICY prediction_results_public_read
ON prediction_results
FOR SELECT
TO anon
USING (
  EXISTS (
    SELECT 1
    FROM match_analyses AS ma
    JOIN daily_matches AS dm ON dm.id = ma.match_id
    WHERE ma.id = prediction_results.analysis_id
      AND dm.is_published = TRUE
  )
);

DROP POLICY IF EXISTS daily_matches_authenticated_all ON daily_matches;
CREATE POLICY daily_matches_authenticated_all
ON daily_matches
FOR ALL
TO authenticated
USING (TRUE)
WITH CHECK (TRUE);

DROP POLICY IF EXISTS match_analyses_authenticated_all ON match_analyses;
CREATE POLICY match_analyses_authenticated_all
ON match_analyses
FOR ALL
TO authenticated
USING (TRUE)
WITH CHECK (TRUE);

DROP POLICY IF EXISTS prediction_results_authenticated_all ON prediction_results;
CREATE POLICY prediction_results_authenticated_all
ON prediction_results
FOR ALL
TO authenticated
USING (TRUE)
WITH CHECK (TRUE);

DROP POLICY IF EXISTS agent_runs_authenticated_all ON agent_runs;
CREATE POLICY agent_runs_authenticated_all
ON agent_runs
FOR ALL
TO authenticated
USING (TRUE)
WITH CHECK (TRUE);

-- service_role biasanya melewati RLS di Supabase. Policy eksplisit ini
-- tetap mendokumentasikan akses penuh sesuai kebutuhan backend.
DROP POLICY IF EXISTS daily_matches_service_role_all ON daily_matches;
CREATE POLICY daily_matches_service_role_all
ON daily_matches
FOR ALL
TO service_role
USING (TRUE)
WITH CHECK (TRUE);

DROP POLICY IF EXISTS match_analyses_service_role_all ON match_analyses;
CREATE POLICY match_analyses_service_role_all
ON match_analyses
FOR ALL
TO service_role
USING (TRUE)
WITH CHECK (TRUE);

DROP POLICY IF EXISTS prediction_results_service_role_all ON prediction_results;
CREATE POLICY prediction_results_service_role_all
ON prediction_results
FOR ALL
TO service_role
USING (TRUE)
WITH CHECK (TRUE);

DROP POLICY IF EXISTS agent_runs_service_role_all ON agent_runs;
CREATE POLICY agent_runs_service_role_all
ON agent_runs
FOR ALL
TO service_role
USING (TRUE)
WITH CHECK (TRUE);
