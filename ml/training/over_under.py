"""Model Over/Under berbasis distribusi Poisson pure Python."""

from __future__ import annotations

import math
from typing import Any


def poisson_pmf(k: int, lam: float) -> float:
    """Menghitung probabilitas P(X=k) pada distribusi Poisson."""
    if k < 0 or lam <= 0:
        return 0.0
    try:
        return (lam**k * math.exp(-lam)) / math.factorial(k)
    except (OverflowError, ValueError):
        return 0.0


def calculate_over_under(home_xg: float, away_xg: float, line: float = 2.5) -> dict[str, Any]:
    """Menghasilkan prediksi Over/Under berdasarkan total expected goals."""
    safe_home = max(0.0, float(home_xg or 0.0))
    safe_away = max(0.0, float(away_xg or 0.0))
    safe_line = max(0.5, float(line or 2.5))
    total_lambda = safe_home + safe_away
    under_limit = int(safe_line)
    under_prob = sum(poisson_pmf(i, total_lambda) for i in range(under_limit + 1))
    under_prob = max(0.0, min(1.0, under_prob))
    over_prob = 1.0 - under_prob
    pick = f"Over {safe_line:g}" if over_prob > under_prob else f"Under {safe_line:g}"
    confidence = round(max(over_prob, under_prob) * 100, 1)
    return {
        "category": "over_under",
        "pick": pick,
        "confidence": confidence,
        "extra": {
            "line": safe_line,
            "over_prob": round(over_prob * 100, 1),
            "under_prob": 
round(under_prob * 100, 1),
        },
    }


if __name__ == "__main__":
    print(calculate_over_under(1.8, 1.2))

