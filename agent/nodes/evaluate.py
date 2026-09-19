"""Node ke-0: mengevaluasi prediksi dari pertandingan yang sudah selesai."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx

from agent.nodes.evaluation_logic import check_correctness


BASE_URL = "https://sports.bzzoiro.com/api/v2"


def _confidence_bucket(confidence: float) -> str:
    """Kelompokkan confidence ke rentang 10%."""
    if confidence >= 90:
        return "90+"
    lower = int(confidence // 10) * 10
    return f"{lower}-{lower + 10}"


def evaluate_predictions(state: dict[str, Any]) -> dict[str, Any]:
    """Evaluasi prediksi dari match yang sudah lewat kickoff dan belum dievaluasi."""
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    api_key = os.getenv("BZZOIRO_API_KEY", "")
    evaluated_count = 0

    if not supabase_url or not service_key:
        state.setdefault("errors", []).append(
            "evaluate: SUPABASE_URL atau SUPABASE_SERVICE_KEY belum dikonfigurasi"
        )
        state["evaluated_count"] = 0
        return state

    supabase_headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    bzzoiro_headers = {"Authorization": f"Token {api_key}", "Accept": "application/json"}

    with httpx.Client(timeout=30) as client:
        try:
            now = datetime.now(timezone.utc).isoformat()

            matches_resp = client.get(
                f"{supabase_url}/rest/v1/daily_matches",
                params={"select": "id,match_id,home_team,away_team,kickoff", "kickoff": f"lt.{now}"},
                headers=supabase_headers,
            )
            matches_resp.raise_for_status()
            past_matches = matches_resp.json()

            for match in past_matches:
                analyses_resp = client.get(
                    f"{supabase_url}/rest/v1/match_analyses",
                    params={"select": "id,category,pick,confidence", "match_id": f"eq.{match['id']}"},
                    headers=supabase_headers,
                )
                analyses_resp.raise_for_status()
                analyses = analyses_resp.json()
                if not analyses:
                    continue

                evaluated_resp = client.get(
                    f"{supabase_url}/rest/v1/prediction_evaluations",
                    params={"select": "analysis_id", "match_id": f"eq.{match['id']}"},
                    headers=supabase_headers,
                )
                evaluated_resp.raise_for_status()
                already_evaluated = {row["analysis_id"] for row in evaluated_resp.json()}

                pending = [a for a in analyses if a["id"] not in already_evaluated]
                if not pending:
                    continue

                event_resp = client.get(f"{BASE_URL}/events/{match['match_id']}/", headers=bzzoiro_headers)
                if event_resp.status_code != 200:
                    continue
                event = event_resp.json()

                if event.get("status") not in ("finished", "closed", "ended"):
                    continue

                home_score = event.get("home_score")
                away_score = event.get("away_score")
                if home_score is None or away_score is None:
                    continue

                for a in pending:
                    is_correct = check_correctness(a["category"], a["pick"], home_score, away_score)
                    insert_resp = client.post(
                        f"{supabase_url}/rest/v1/prediction_evaluations",
                        headers=supabase_headers,
                        json={
                            "analysis_id": a["id"],
                            "match_id": match["id"],
                            "category": a["category"],
                            "predicted_pick": a["pick"],
                            "predicted_confidence": a["confidence"],
                            "confidence_bucket": _confidence_bucket(a["confidence"]),
                            "actual_home_score": home_score,
                            "actual_away_score": away_score,
                            "actual_result": f"{home_score}-{away_score}",
                            "is_correct": is_correct,
                        },
                    )
                    insert_resp.raise_for_status()
                    evaluated_count += 1

        except Exception as exc:
            state.setdefault("errors", []).append(f"evaluate: {exc}")

    state["evaluated_count"] = evaluated_count
    return state
