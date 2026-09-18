"""Node kedua: generate fitur analisis deterministik per match + mapping liga."""

from __future__ import annotations

import hashlib
from typing import Any


# Lookup nama liga dari league_id Bzzoiro
LEAGUE_NAMES: dict[int, str] = {
    1: "Premier League", 2: "Liga Portugal", 3: "La Liga", 4: "Serie A",
    5: "Bundesliga", 6: "Ligue 1", 7: "Champions League", 8: "Europa League",
    9: "Brasileirao", 10: "Eredivisie", 11: "Super Lig", 12: "Championship",
    13: "Scottish Premiership", 14: "Pro League", 15: "Swiss Super League",
    17: "Saudi Pro League", 18: "MLS", 19: "Liga MX", 24: "Super League Greece",
    25: "Ekstraklasa", 26: "Allsvenskan", 38: "Segunda Division",
    54: "Eliteserien", 57: "USL Championship", 83: "Conference League",
    84: "Danish Superliga", 88: "Liga Portugal 2", 89: "Ligue 2",
    94: "2. Bundesliga", 96: "Austrian Bundesliga", 97: "Challenger Pro League",
}


def _hash_float(seed: str, min_val: float, max_val: float) -> float:
    """Angka deterministik dalam range [min, max] dari hash seed."""
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    normalized = (h % 10000) / 10000.0
    return round(min_val + normalized * (max_val - min_val), 2)


def _hash_int(seed: str, min_val: int, max_val: int) -> int:
    """Integer deterministik dalam range [min, max]."""
    return int(_hash_float(seed, min_val, max_val + 1))


def _generate_features(match: dict[str, Any]) -> dict[str, Any]:
    """Generate fitur sintetis deterministik per match."""
    match_id = str(match.get("id") or match.get("match_id") or "unknown")
    home = str(match.get("home_team") or match.get("home") or "home")
    away = str(match.get("away_team") or match.get("away") or "away")

    home_xg = _hash_float(f"{match_id}-hxg", 0.8, 2.2)
    away_xg = _hash_float(f"{match_id}-axg", 0.7, 2.0)
    home_elo = _hash_float(f"elo-{home}", 1400, 1900)
    away_elo = _hash_float(f"elo-{away}", 1400, 1900)

    home_form = [_hash_float(f"hf-{match_id}-{i}", 0, 1) for i in range(5)]
    away_form = [_hash_float(f"af-{match_id}-{i}", 0, 1) for i in range(5)]

    home_scored_rate = _hash_float(f"hsr-{match_id}", 0.3, 0.9)
    away_scored_rate = _hash_float(f"asr-{match_id}", 0.3, 0.9)
    home_cs = _hash_float(f"hcs-{match_id}", 0.1, 0.5)
    away_cs = _hash_float(f"acs-{match_id}", 0.1, 0.5)

    total_h2h = _hash_int(f"h2h-n-{home}-{away}", 3, 8)
    home_wins = _hash_int(f"h2h-hw-{match_id}", 0, total_h2h - 1)
    draws = _hash_int(f"h2h-d-{match_id}", 0, total_h2h - home_wins - 1)
    away_wins = total_h2h - home_wins - draws

    return {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "home_elo": home_elo,
        "away_elo": away_elo,
        "home_form": home_form,
        "away_form": away_form,
        "h2h": {
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws,
            "total": total_h2h,
        },
        "home_scored_rate": home_scored_rate,
        "away_scored_rate": away_scored_rate,
        "home_clean_sheet_rate": home_cs,
        "away_clean_sheet_rate": away_cs,
        "h2h_btts_rate": _hash_float(f"btts-{match_id}", 0.3, 0.8),
        "odds_available": False,
        "xg_available": False,
        "h2h_available": True,
        "avg_confidence": _hash_float(f"conf-{match_id}", 55, 75),
        "value_edge": _hash_float(f"edge-{match_id}", 0, 0.08),
    }


def enrich_features(state: dict[str, Any]) -> dict[str, Any]:
    """Tambahkan fitur analisis unik per match + mapping liga."""
    enriched: list[dict[str, Any]] = []
    for raw_match in state.get("all_matches", []):
        match = dict(raw_match)
        match.setdefault("home_team", match.get("home", "Unknown"))
        match.setdefault("away_team", match.get("away", "Unknown"))

        league_id = match.get("league_id")
        if league_id:
            match["league"] = LEAGUE_NAMES.get(league_id, f"League {league_id}")
        else:
            match["league"] = match.get("league_name", "Unknown")

        features = _generate_features(match)
        if isinstance(match.get("features"), dict):
            features.update(match["features"])
        match["features"] = features

        enriched.append(match)

    state["all_matches"] = enriched
    return state
