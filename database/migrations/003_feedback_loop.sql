-- File: 003_feedback_loop.sql
-- Deskripsi: Setup feedback loop untuk tracking akurasi prediksi.
-- Versi: v1.0.0
-- Dibuat: 2026-10-03

-- Index untuk query evaluasi cepat di prediction_results
CREATE INDEX IF NOT EXISTS idx_pred_results_analysis
  ON prediction_results(analysis_id);

CREATE INDEX IF NOT EXISTS idx_pred_results_evaluated
  ON prediction_results(evaluated_at DESC);

CREATE INDEX IF NOT EXISTS idx_pred_results_correct
  ON prediction_results(is_correct);

-- View ringkasan akurasi per kategori + confidence bucket
CREATE OR REPLACE VIEW view_accuracy_confidence AS
SELECT
  COALESCE(ma.category, 'unknown') AS category,
  CASE
    WHEN ma.confidence IS NULL THEN 'unknown'
    WHEN ma.confidence >= 90 THEN '90+'
    ELSE CONCAT((FLOOR(ma.confidence / 10) * 10)::INT, '-', ((FLOOR(ma.confidence / 10) * 10) + 10)::INT)
  END AS confidence_bucket,
  COUNT(*) AS total,
  SUM(CASE WHEN pr.is_correct THEN 1 ELSE 0 END) AS correct,
  ROUND(
    100.0 * SUM(CASE WHEN pr.is_correct THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
    1
  ) AS accuracy_pct,
  MIN(pr.evaluated_at) AS first_evaluated,
  MAX(pr.evaluated_at) AS last_evaluated
FROM prediction_results pr
LEFT JOIN match_analyses ma ON ma.id = pr.analysis_id
WHERE pr.is_correct IS NOT NULL
GROUP BY category, confidence_bucket
ORDER BY category, confidence_bucket;

-- Grant akses (kalau RLS aktif, view ini public read)
GRANT SELECT ON view_accuracy_confidence TO anon;
GRANT SELECT ON view_accuracy_confidence TO authenticated;
