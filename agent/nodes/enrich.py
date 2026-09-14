"""Node kedua: menambahkan fitur analisis dengan fallback defensif."""

from __future__ import annotations

from typing import Any


DEFAULT_FEATURES: dict[str, Any] = {
    "home_xg": 1.3,
    "away_xg": 1.1,
    "home_elo": 1500.0,
    "away_elo": 1500.0,
    "home_form": [1, 1, 0, 0, 1],
    "away_form": [0, 1, 1, 0, 0],
    "h2h": {"home_wins": 0, "total": 0, "draws": 0},
    "home_scored_rate": 0.6,
    "away_scored_rate": 0.5,
    "home_clean_sheet_rate": 0.3,
    "away_clean_sheet_rate": 0.3,
    "h2h_btts_rate": 0.5,
    "odds_available": False,
    "xg_available": False,
    "h2h_available": False,
    "avg_confidence": 65.0,
    "value_edge": 0.0,
}


def enrich_features(state: dict[str, Any]) -> dict[str, Any]:
    """Tambahkan xG, form, H2H, odds, confidence, dan value edge ke fixtures."""
    enriched: list[dict[str, Any]] = []
    for raw_match in state.get("all_matches", []):
        match = dict(raw_match)
        features = dict(DEFAULT_FEATURES)
        features.update(match.get("features") or {})
        match["features"] = features
        match.setdefault("league", match.get("league_name", "Unknown"))
        match.setdefault("home_team", match.get("home", "Unknown"))
        match.setdefault("away_team", match.get("away", "Unknown"))
        enriched.append(match)
    state["all_matches"] = enriched
    return state
