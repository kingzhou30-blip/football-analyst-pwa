"""Skema data dan helper transformasi response backend Football Analyst PWA."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class MatchAnalysis:
    """Representasi satu analisis prediksi pertandingan."""

    category: str
    pick: str
    confidence: float | None = None
    odds: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    reason: str | None = None


@dataclass(slots=True)
class MatchSummary:
    """Representasi ringkas pertandingan yang dikirim ke frontend."""

    id: str
    match_id: str
    league: str
    kickoff: str
    home_team: str
    away_team: str
    match_score: float | None = None
    agent_insight: str | None = None
    analyses: list[MatchAnalysis] = field(default_factory=list)


def _number(value: Any) -> float | None:
    """Mengubah nilai numerik dari REST API menjadi float yang aman."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_analysis(row: Mapping[str, Any]) -> dict[str, Any]:
    """Menormalisasi satu row analisis menjadi dictionary JSON."""
    return {
        "id": row.get("id"),
        "category": row.get("category"),
        "pick": row.get("pick"),
        "confidence": _number(row.get("confidence")),
        "odds": _number(row.get("odds")),
        "extra": row.get("extra") or {},
        "reason": row.get("reason"),
        "created_at": row.get("created_at"),
    }


def format_match(row: Mapping[str, Any], analyses: list[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Menormalisasi row pertandingan dan menggabungkan analisisnya."""
    return {
        "id": row.get("id"),
        "match_id": row.get("match_id"),
        "league": row.get("league"),
        "league_code": row.get("league_code"),
        "kickoff": row.get("kickoff"),
        "home_team": row.get("home_team"),
        "away_team": row.get("away_team"),
        "home_team_id": row.get("home_team_id"),
        "away_team_id": row.get("away_team_id"),
        "match_score": _number(row.get("match_score")),
        "agent_insight": row.get("agent_insight"),
        "model_version": row.get("model_version"),
        "is_published": row.get("is_published", True),
        "generated_at": row.get("generated_at"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "analyses": [format_analysis(item) for item in (analyses or [])],
    }


def format_prediction_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Menormalisasi row dari view_daily_predictions menjadi response frontend."""
    return {
        "daily_match_id": row.get("daily_match_id"),
        "external_match_id": row.get("external_match_id"),
        "league": row.get("league"),
        "league_code": row.get("league_code"),
        "kickoff": row.get("kickoff"),
        "home_team": row.get("home_team"),
        "away_team": row.get("away_team"),
        "match_score": _number(row.get("match_score")),
        "agent_insight": row.get("agent_insight"), "model_version": row.get("model_version"),
        "analysis": format_analysis(row),
    }
