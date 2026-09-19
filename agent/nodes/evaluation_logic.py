"""Logic evaluasi kebenaran prediksi berdasarkan skor akhir pertandingan."""

from __future__ import annotations

import re
from typing import Optional


def check_correctness(category: str, pick: str, home_score: int, away_score: int) -> Optional[bool]:
    """Menentukan apakah prediksi benar. Return None jika hasil 'push' (tidak dihitung)."""
    total = home_score + away_score

    if category == "over_under":
        match = re.search(r'(\d+\.?\d*)', pick)
        if not match:
            return None
        line = float(match.group(1))
        if "Over" in pick:
            return total > line
        if "Under" in pick:
            return total < line
        return None

    if category == "btts":
        btts_happened = home_score > 0 and away_score > 0
        if "Yes" in pick:
            return btts_happened
        if "No" in pick:
            return not btts_happened
        return None

    if category == "win":
        if "Home" in pick:
            return home_score > away_score
        if "Away" in pick:
            return away_score > home_score
        if "Draw" in pick:
            return home_score == away_score
        return None

    if category == "handicap":
        match = re.search(r'([+-]?\d+\.?\d*)', pick)
        line = float(match.group(1)) if match else 0.0
        if "Home" in pick:
            adjusted_diff = (home_score - away_score) + line
        elif "Away" in pick:
            adjusted_diff = (away_score - home_score) + line
        else:
            return None
        if adjusted_diff > 0:
            return True
        if adjusted_diff == 0:
            return None
        return False

    return None
