"""Selector pertandingan dengan skor kelayakan 0 sampai 100."""

from __future__ import annotations

from statistics import mean
from typing import Any, Mapping, Sequence


TOP_LEAGUES = [
    "EPL",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "Champions League",
    "Europa League",
]


def _value(features: Mapping[str, Any], key: str, default: Any = False) -> Any:
    """Mengambil feature dengan default aman."""
    return features.get(key, default)


def calculate_match_score(match: Mapping[str, Any], features: Mapping[str, Any]) -> float:
    """Menghitung skor kelayakan pertandingan pada rentang 0 sampai 100."""
    completeness = (
        10 if _value(features, "xg_available") else 0
    ) + (
        8 if _value(features, "h2h_available") else 0
    ) + (
        7 if _value(features, "odds_available") else 0
    )
    league = str(match.get("league_code") or match.get("league") or "")
    if league in TOP_LEAGUES:
        league_score = 20
    elif league:
        league_score = 10
    else:
        league_score = 0
    confidences = _value(features, "confidences", []) or []
    try:
        avg_confidence = mean(float(value) for value in confidences) if confidences else float(_value(features, "avg_confidence", 0) or 0)
    except (TypeError, ValueError, ArithmeticError):
        avg_confidence = 0.0
    confidence_score = max(0.0, min(25.0, avg_confidence / 100 * 25))
    try:
        value_edge = float(_value(features, "value_edge", 0) or 0)
    except (TypeError, ValueError):
        value_edge = 0.0
    if value_edge > 0.05:
        value_score = 30
    elif value_edge > 0.02:
        value_score = 15
    else:
        value_score = 0
    return round(max(0.0, min(100.0, completeness + league_score + confidence_score + value_score)), 1)


def select_top_matches(all_matches: Sequence[Mapping[str, Any]], top_n: int = 7) -> list[dict[str, Any]]:
    """Memilih maksimal top_n pertandingan dengan minimal skor 60 dan dua per liga."""
    safe_top_n = max(0, int(top_n))
    if safe_top_n == 0:
        return []
    scored: list[dict[str, Any]] = []
    for item in all_matches or []:
        match = dict(item)
        features = match.get("features") or {}
        match_score = calculate_match_score(match, features)
        if match_score >= 60:
            match["match_score"] = match_score
            scored.append(match)
    scored.sort(key=lambda row: row.get("match_score", 0), reverse=True)
    selected: list[dict[str, Any]] = []
    league_counts: dict[str, int] = {}
    for match in scored:
        league = str(match.get("league_code") or match.get("league") or "Unknown")
        if league_counts.get(league, 0) >= 2:
            continue
        selected.append(match)
        league_counts[league] = league_counts.get(league, 0) + 1
        if len(selected) >= safe_top_n:
            break
    return selected


if __name__ == "__main__":
    sample = {
        "league_code": "EPL",
        "features": {
            "xg_available": True,
            "h2h_available": True,
            "odds_available": True,
            "confidences": [75, 72, 68, 70],
            "value_edge": 0.06,
        },
    }
    print(calculate_match_score(sample,
sample["features"]))
    print(select_top_matches([sample]))
