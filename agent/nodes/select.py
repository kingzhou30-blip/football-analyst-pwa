"""Node ketiga: memilih maksimal tujuh pertandingan terbaik."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ML_PATH = Path(__file__).resolve().parents[2] / "ml"
if str(ML_PATH) not in sys.path:
    sys.path.insert(0, str(ML_PATH))

from training.match_selector import select_top_matches


def select_top(state: dict[str, Any]) -> dict[str, Any]:
    """Pilih pertandingan dengan skor minimal 60 dan maksimal dua per liga."""
    try:
        state["selected_matches"] = select_top_matches(state.get("all_matches", []), top_n=7)
    except Exception as exc:
        state.setdefault("errors", []).append(f"select: {exc}")
        state["selected_matches"] = []
    return state
