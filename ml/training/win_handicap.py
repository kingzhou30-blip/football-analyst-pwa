"""Model prediksi kemenangan dan Asian Handicap pure Python."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def _form_average(values: Sequence[float] | None) -> float:
    """Menghitung rata-rata form atau memakai nilai netral jika kosong."""
    if not values:
        return 0.5
    clean_values = []
    for value in values:
        try:
            clean_values.append(max(0.0, min(1.0, float(value))))
        except (TypeError, ValueError):
            continue
    return sum(clean_values) / len(clean_values) if clean_values else 0.5


def calculate_win(
    home_elo: float,
    away_elo: float,
    home_form: Sequence[float] | None,
    away_form: Sequence[float] | None,
    h2h: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Menghasilkan prediksi Home Win, Draw, atau Away Win."""
    try:
        elo_diff = float(home_elo) - float(away_elo) + 100
    except (TypeError, ValueError):
        elo_diff = 100.0
    elo_home_prob = 1 / (1 + 10 ** (-elo_diff / 400))
    form_home = _form_average(home_form)
    form_away = _form_average(away_form)
    form_diff = (form_home - form_away) * 0.3
    record = h2h or {}
    try:
        total = max(float(record.get("total", 1) or 1), 1.0)
        home_wins = max(float(record.get("home_wins", 0) or 0), 0.0)
    except (TypeError, ValueError):
        total, home_wins = 1.0, 0.0
    h2h_home = min(1.0, home_wins / total)
    home_win = elo_home_prob * 0.5 + (0.5 + form_diff) * 0.3 + h2h_home * 0.2
    draw = 0.25
    away_win = max(0.01, 1 - home_win - draw)
    total_probability = home_win + draw + away_win
    home_win /= total_probability
    draw /= total_probability
    away_win /= total_probability
    probabilities = {"Home Win": home_win, "Draw": draw, "Away Win": away_win}
    pick = max(probabilities, key=probabilities.get)
    return {
        "category": "win",
        "pick": pick,
        "confidence": round(max(probabilities.values()) * 100, 1),
        "extra": {
            "home_win": round(home_win * 100, 1),
            "draw": round(draw * 100, 1),
            "away_win": round(away_win * 100, 1),
        },
    }


def calculate_handicap(home_xg: float, away_xg: float) -> dict[str, Any]:
    """Memetakan selisih xG ke rekomendasi garis Asian Handicap."""
    try:
        xg_diff = float(home_xg) - float(away_xg)
    except (TypeError, ValueError):
        xg_diff = 0.0
    if xg_diff >= 1.5:
        line, pick = -1.5, "Home -1.5"
    elif xg_diff >= 1.0:
        line, pick = -1.0, "Home -1.0"
    elif xg_diff >= 0.5:
        line, pick = -0.5, "Home -0.5"
    elif xg_diff >= 0:
        line, pick = 0.0, "Home 0 (Draw No Bet)"
    elif xg_diff >= -0.5:
        line, pick = 0.5, "Away +0.5"
    elif xg_diff >= -1.0:
        line, pick = 1.0, "Away +1.0"
    else:
        line, pick = 1.5, "Away +1.5"
    confidence = min(95.0, 60.0 + abs(xg_diff) * 20.0)
    return {
        "category": "handicap",
        "pick": pick,
        "confidence": round(confidence, 1),
        "extra": {"line": line, "xg_diff": round(xg_diff, 2)},
    }


if __name__ == "__main__":
    print(calculate_win(1550, 1500, [1, 1, 0.5, 1, 0.5], [0.5, 0, 1, 0.5, 0.5],
{"home_wins": 3, "total": 6, "draws": 1}))
    print(calculate_handicap(1.7, 1.1))
