"""Node kelima: membuat narasi insight melalui OpenRouter com fallback lokal."""

from __future__ import annotations

import os
from typing import Any

import httpx


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-exp:free"

def _fallback_insight(match: dict[str, Any], analysis: dict[str, Any]) -> str:
    """Membuat insight deterministik ketika LLM tidak tersedia."""
    home = match.get("home_team", "Home")
    away = match.get("away_team", "Away")
    over_under = analysis["over_under"]
    btts = analysis["btts"]
    return (
        f"{home} vs {away}: {over_under['pick']} dengan confidence {over_under['confidence']}%. "
        f"Model BTTS memilih {btts['pick']} dengan confidence {btts['confidence']}%."
    )


def generate_insight(state: dict[str, Any]) -> dict[str, Any]:
    """Generate narasi dua kalimat untuk setiap analisis dengan fallback lokal."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    for analysis in state.get("analyses", []):
        match = analysis.get("match_data", {})
        prompt = (
            f"Analisis pertandingan {match.get('home_team', 'Home')} vs {match.get('away_team', 'Away')}. "
            f"Prediksi: Over/Under={analysis['over_under']['pick']}, "
            f"BTTS={analysis['btts']['pick']}, Win={analysis['win']['pick']}, "
            f"Handicap={analysis['handicap']['pick']}. "
            "Buat narasi analisis singkat 2 kalimat dalam Bahasa Indonesia."
        )
        try:
            if not api_key:
                raise RuntimeError("OPENROUTER_API_KEY belum dikonfigurasi")
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    OPENROUTER_URL,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]},
                )
                response.raise_for_status()
                payload = response.json()
                insight = payload["choices"][0]["message"]["content"]
                analysis["agent_insight"] = str(insight).strip()
        except Exception as exc:
            analysis["agent_insight"] = _fallback_insight(match, analysis)
            state.setdefault("errors", []).append(f"insight: {exc}")
    return state
