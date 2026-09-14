"""Selector pertandingan dengan skor kelayakan 0 sampai 100."""

from __future__ import annotations

from statistics import mean
from typing import Any, Mapping, Sequence


# Liga populer & menengah yang datanya lengkap dan pasarnya likuid.
# Cakupan: top-5 Eropa, kompetisi UEFA, liga Skandinavia,
# kejuaraan Inggris, dan Bundesliga 2.
TOP_LEAGUES = [
    # Top-5 Eropa
    "EPL",
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    # Kompetisi UEFA
    "Champions League",
    "UCL",
    "Europa League",
    "UEL",
    "Conference League",
    "UECL",
    # Liga menengah Eropa
    "Eredivisie",
    "Eerste Divisie",
    "English Championship",
    "Championship",
    "EFL Championship",
    "Bundesliga 2",
    "2. Bundesliga",
    # Skandinavia
    "Allsvenskan",
    "Eliteserien",
    # Liga Portugal, Belgia, Turki, Skotlandia
    "Primeira Liga",
    "Liga Portugal",
    "Jupiler Pro League",
    "Süper Lig",
    "Super Lig",
    "Scottish Premiership",
    "MLS",
    "Liga MX",
]

# Threshold minimum skor kelayakan.
# Default 60 terlalu ketat untuk data Bzzoiro free tier yang
# sering tanpa xG/H2H/odds. Turunkan ke 20 agar tetap ada
# pertandingan yang terpilih.
MIN_MATCH_SCORE = 20.0


def _value(features: Mapping[str, Any], key: str, default: Any = False) -> Any:
    """Mengambil feature dengan default aman."""
    return features.get(key, default)


def _normalize_league(match: Mapping[str, Any]) -> str:
    """Ambil nama liga dari berbagai kemungkinan field."""
    return str(
        match.get("league")
        or match.get("league_name")
        or match.get("league_code")
        or ""
    ).strip()


def _is_top_league(league: str) -> bool:
    """Cek apakah liga termasuk dalam TOP_LEAGUES (case-insensitive)."""
    if not league:
        return False
    league_lower = league.lower()
    for top in TOP_LEAGUES:
        if top.lower() in league_lower or league_lower in top.lower():
            return True
    return False


def calculate_match_score(
    match: Mapping[str, Any],
    features: Mapping[str, Any],
) -> float:
    """Menghitung skor kelayakan pertandingan pada rentang 0 sampai 100.

    Komponen skor:
    - Kelengkapan data (xG, H2H, odds): maks 25
    - Liga populer: maks 20
    - Confidence rata-rata: maks 25
    - Value edge vs odds pasar: maks 30
    """
    # 1. Kelengkapan data (0-25)
    completeness = (
        (10 if _value(features, "xg_available") else 0)
        + (8 if _value(features, "h2h_available") else 0)
        + (7 if _value(features, "odds_available") else 0)
    )

    # 2. Liga populer (0-20)
    league = _normalize_league(match)
    if _is_top_league(league):
        league_score = 20.0
    elif league:
        league_score = 10.0
    else:
        league_score = 0.0

    # 3. Confidence rata-rata (0-25)
    confidences: Sequence[float] = _value(features, "confidences", []) or []
    if confidences:
        try:
            avg_confidence = float(mean(confidences))
        except (TypeError, ValueError):
            avg_confidence = 0.0
    else:
        avg_confidence = float(_value(features, "avg_confidence", 65.0))
    confidence_score = max(0.0, min(avg_confidence, 100.0)) / 100.0 * 25.0

    # 4. Value edge vs odds (0-30)
    value_edge = float(_value(features, "value_edge", 0.0) or 0.0)
    if value_edge > 0.05:
        edge_score = 30.0
    elif value_edge > 0.02:
        edge_score = 15.0
    else:
        edge_score = 0.0

    total = completeness + league_score + confidence_score + edge_score
    return round(max(0.0, min(total, 100.0)), 2)


def select_top_matches(
    all_matches: Sequence[Mapping[str, Any]],
    top_n: int = 7,
) -> list[Mapping[str, Any]]:
    """Pilih pertandingan dengan skor minimal MIN_MATCH_SCORE.

    Aturan:
    - Skor minimal MIN_MATCH_SCORE (default 20).
    - Urutkan menurun berdasarkan skor.
    - Maksimal dua pertandingan per liga untuk variasi.
    - Ambil paling banyak top_n pertandingan.
    - Kalau semua di bawah threshold, tetap ambil top_n teratas
      sebagai fallback agar pipeline tidak kosong.
    """
    if not all_matches or top_n <= 0:
        return []

    scored: list[dict[str, Any]] = []
    for match in all_matches:
        features = dict(match.get("features") or {})
        score = calculate_match_score(match, features)
        entry = dict(match)
        entry["match_score"] = score
        scored.append(entry)

    # Filter yang memenuhi threshold
    qualified = [m for m in scored if m["match_score"] >= MIN_MATCH_SCORE]

    # Fallback: kalau tidak ada yang lolos, ambil semua
    if not qualified:
        qualified = scored

    # Sort menurun
    qualified.sort(key=lambda m: m["match_score"], reverse=True)

    # Ambil maksimal dua per liga
    selected: list[Mapping[str, Any]] = []
    league_count: dict[str, int] = {}
    for match in qualified:
        league = _normalize_league(match) or "Unknown"
        if league_count.get(league, 0) < 2:
            selected.append(match)
            league_count[league] = league_count.get(league, 0) + 1
        if len(selected) >= top_n:
            break

    # Kalau masih kurang dari top_n, isi dari qualified tanpa
    # batas per liga
    if len(selected) < top_n:
        for match in qualified:
            if match not in selected:
                selected.append(match)
            if len(selected) >= top_n:
                break

    return selected
