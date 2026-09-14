"""Node keempat: menjalankan empat model prediksi pada pertandingan terpilih."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ML_PATH = Path(__file__).resolve().parents[2] / "ml"
if str(ML_PATH) not in sys.path:
    sys.path.insert(0, str(ML_PATH))

from training.btts import calculate_btts
from training.over_under import calculate_over_under
from training.win_handicap import calculate_handicap, calculate_win


def analyze_matches(state: dict[str, Any]) -> dict[str, Any]:
    """Jalankan Over/Under, BTTS, Win, dan Handicap untuk setiap match."""
    analyses: list[dict[str, Any]] = []
    for match in state.get("selected_matches", []):
        features = match.get("features", {})
        try:
            home_xg = features.get("home_xg", 1.3)
            away_xg = features.get("away_xg", 1.1)
            analysis = {
                "match_id": match.get("id"),
                "match_data": match,
                "over_under": calculate_over_under(home_xg, away_xg),
                "btts": calculate_btts(
                    home_xg,
                    away_xg,
                    features.get("home_scored_rate", 0.6),
                    features.get("away_scored_rate", 0.5),
                    features.get("home_clean_sheet_rate", 0.3),
                    features.get("away_clean_sheet_rate", 0.3),
                    features.get("h2h_btts_rate", 0.5),
                ),
                "win": calculate_win(
                    features.get("home_elo", 1500),
                    features.get("away_elo", 1500),
                    features.get("home_form", [1, 1, 0, 0, 1]),
                    features.get("away_form", [0, 1, 1, 0, 0]),
                    features.get("h2h", {"home_wins": 0, "total": 0}),
                ),
                "handicap": calculate_handicap(home_xg, away_xg),
            }
            analyses.append(analysis)
        except Exception as exc:
            state.setdefault("errors", []).append(f"analyze: {exc}")
    state["analyses"] = analyses
    return state
