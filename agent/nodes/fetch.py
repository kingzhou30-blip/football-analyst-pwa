"""Node pertama: mengambil fixtures bola hari ini dari Bzzoiro API."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import httpx


BASE_URL = "https://sports.bzzoiro.com/api/v2"


def fetch_fixtures(state: dict[str, Any]) -> dict[str, Any]:
    """Ambil fixtures bola hari ini dan simpan hasilnya ke state."""
    api_key = os.getenv("BZZOIRO_API_KEY")
    target_date = date.today().isoformat()
    try:
        if not api_key:
            raise RuntimeError("BZZOIRO_API_KEY belum dikonfigurasi")
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{BASE_URL}/events/",
                params={"date_from": target_date, "date_to": target_date},
                headers={"Authorization": f"Token {api_key}", "Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                matches = data.get("results", data.get("data", []))
            else:
                matches = data
            state["all_matches"] = matches if isinstance(matches, list) else []
    except Exception as exc:
        state.setdefault("errors", []).append(f"fetch: {exc}")
        state["all_matches"] = []
    return state
