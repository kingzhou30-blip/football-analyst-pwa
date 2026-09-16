"""Node pertama: mengambil fixtures bola hari ini dari Bzzoiro API."""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import httpx


BASE_URL = "https://sports.bzzoiro.com/api/v2"

# Hanya liga-liga berikut yang akan dianalisis agent.
# Daftar dipilih agar data statistik (H2H, odds) lebih lengkap dan relevan.
ALLOWED_LEAGUE_IDS: set[int] = {
    # === Top 5 Eropa ===
    1,   # Premier League (England)
    3,   # La Liga (Spain)
    4,   # Serie A (Italy)
    5,   # Bundesliga (Germany)
    6,   # Ligue 1 (France)
    # === Sekunder Portugal & Belanda ===
    2,   # Liga Portugal Betclic
    10,  # Eredivisie (Netherlands)
    # === Kompetisi Eropa Antar-klub ===
    7,   # UEFA Champions League
    8,   # UEFA Europa League
    83,  # UEFA Conference League
    # === Divisi 2 / Kasta Kedua Eropa ===
    12,  # Championship (England)
    94,  # 2. Bundesliga (Germany)
    89,  # Ligue 2 (France)
    38,  # Segunda División (Spain)
    88,  # Liga Portugal 2
    # === Liga Populer Eropa & Global ===
    96,  # Austrian Bundesliga
    14,  # Pro League (Belgium)
    84,  # Danish Superliga
    24,  # Stoiximan Super League (Greece)
    25,  # Ekstraklasa (Poland)
    13,  # Scottish Premiership
    26,  # Allsvenskan (Sweden)
    15,  # Super League (Switzerland)
    11,  # Trendyol Super Lig (Turkey)
    17,  # Saudi Pro League
}


def fetch_fixtures(state: dict[str, Any]) -> dict[str, Any]:
    """Ambil fixtures bola hari ini dan simpan hasilnya ke state, difilter ke liga terpilih."""
    api_key = os.getenv("BZZOIRO_API_KEY")
    # Fetch range 3 hari ke depan (UTC) untuk coverage lebih baik
    target_date = date.today().isoformat()
    end_date = (date.today() + timedelta(days=3)).isoformat()
    try:
        if not api_key:
            raise RuntimeError("BZZOIRO_API_KEY belum dikonfigurasi")
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{BASE_URL}/events/",
                params={"date_from": target_date, "date_to": end_date},
                headers={"Authorization": f"Token {api_key}", "Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                matches = data.get("results", data.get("data", []))
            else:
                matches = data
            if not isinstance(matches, list):
                matches = []
            filtered = [m for m in matches if m.get("league_id") in ALLOWED_LEAGUE_IDS]
            state["all_matches"] = filtered
    except Exception as exc:
        state.setdefault("errors", []).append(f"fetch: {exc}")
        state["all_matches"] = []
    return state
