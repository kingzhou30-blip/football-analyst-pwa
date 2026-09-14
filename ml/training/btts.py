"""Model BTTS berbasis expected goals dan fitur statistik sederhana."""

from __future__ import annotations

import math
from typing import Any


def _bounded(value: float | None, default: float = 0.0) -> float:
    """Mengubah nilai menjadi probabilitas di antara nol dan satu."""
    try:
        return max(0.0, min(1.0, float(value if value is not None else default)))
    except (TypeError, ValueError):
        return default


def calculate_btts(
    home_xg: float,
    away_xg: float,
    home_scored_rate: float,
    away_scored_rate: float,
    home_clean_sheet_rate: float,
    away_clean_sheet_rate: float,
    h2h_btts_rate: float,
) -> dict[str, Any]:
    """Menghasilkan prediksi BTTS Yes/No dari tujuh fitur input."""
    safe_home_xg = max(0.0, float(home_xg or 0.0))
    safe_away_xg = max(0.0, float(away_xg or 0.0))
    p_home_scores = 1 - math.exp(-safe_home_xg * 1.2)
    p_away_scores = 1 - math.exp(-safe_away_xg * 1.0)
    form_factor = (_bounded(home_scored_rate) + _bounded(away_scored_rate)) / 2
    defence_weakness = 1 - (_bounded(home_clean_sheet_rate) + _bounded(away_clean_sheet_rate)) / 2
    p_btts = (
        p_home_scores * p_away_scores * 0.5
        + form_factor * 0.2
        + defence_weakness * 0.15
        + _bounded(h2h_btts_rate) * 0.15
    )
    p_btts = max(0.0, min(1.0, p_btts))
    return {
        "category": "btts",
        "pick": "BTTS Yes" if p_btts > 0.5 else "BTTS No",
        "confidence": round(max(p_btts, 
1 - p_btts) * 100, 1),
        "extra": {
            "btts_yes": round(p_btts * 100, 1),
            "btts_no": round((1 - p_btts) * 100, 1),
        },
    }


if __name__ == "__main__":
    print(calculate_btts(1.6, 1.3, 0.8, 0.75, 0.25, 0.3, 0.7))

