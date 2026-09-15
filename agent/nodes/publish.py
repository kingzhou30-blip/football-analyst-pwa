"""Node keenam: menyimpan hasil agent ke tabel Supabase melalui REST API."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx


# Confidence minimum untuk kategori yang layak dipublikasikan.
# Prediksi di bawah threshold ini dianggap terlalu tidak pasti
# dan dibuang agar akurasi keseluruhan meningkat.
MIN_CATEGORY_CONFIDENCE = 60.0


def publish_to_supabase(state: dict[str, Any]) -> dict[str, Any]:
    """Simpan daily_matches dan empat match_analyses ke Supabase."""
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    published_count = 0

    if not supabase_url or not service_key:
        state.setdefault("errors", []).append(
            "publish: SUPABASE_URL atau SUPABASE_SERVICE_KEY belum dikonfigurasi"
        )
        state["published_count"] = 0
        return state

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=merge-duplicates",
    }

    with httpx.Client(timeout=30) as client:
        for analysis in state.get("analyses", []):
            match = analysis.get("match_data", {})
            try:
                external_id = str(match.get("id") or match.get("match_id"))
                match_row = {
                    "match_id": external_id,
                    "league": match.get("league", "Unknown"),
                    "league_code": match.get("league_code"),
                    "kickoff": match.get("event_date", datetime.now(timezone.utc).isoformat()),
                    "home_team": match.get("home_team", ""),
                    "away_team": match.get("away_team", ""),
                    "home_team_id": str(match.get("home_team_id")) if match.get("home_team_id") else None,
                    "away_team_id": str(match.get("away_team_id")) if match.get("away_team_id") else None,
                    "match_score": match.get("match_score", 0),
                    "agent_insight": analysis.get("agent_insight", ""),
                    "model_version": "v1.0.0",
                    "is_published": True,
                }
                response = client.post(
                    f"{supabase_url}/rest/v1/daily_matches?on_conflict=match_id",
                    headers=headers,
                    json=match_row,
                )
                response.raise_for_status()
                inserted = response.json()

                if not isinstance(inserted, list) or not inserted:
                    raise RuntimeError("Supabase tidak mengembalikan daily_match")

                daily_match_id = inserted[0]["id"]

                for category in ("over_under", "btts", "win", "handicap"):
                    category_data = analysis[category]

                    # Skip kategori dengan confidence di bawah threshold
                    if category_data.get("confidence", 0) < MIN_CATEGORY_CONFIDENCE:
                        continue

                    analysis_response = client.post(
                        f"{supabase_url}/rest/v1/match_analyses",
                        headers=headers,
                        json={
                            "match_id": daily_match_id,
                            "category": category_data["category"],
                            "pick": category_data["pick"],
                            "confidence": category_data["confidence"],
                            "odds": category_data.get("odds"),
                            "extra": category_data.get("extra", {}),
                            "reason": category_data.get("reason"),
                        },
                    )
                    # Skip 409 Conflict — data sudah ada (duplikat)
                    if analysis_response.status_code == 409:
                        continue
                    analysis_response.raise_for_status()

                published_count += 1
            except Exception as exc:
                state.setdefault("errors", []).append(f"publish: {exc}")

    state["published_count"] = published_count
    return state
