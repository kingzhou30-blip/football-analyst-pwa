"""Entry point untuk menjalankan agent analisis harian enam node."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


AGENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AGENT_DIR.parent

load_dotenv(PROJECT_ROOT / "backend" / ".env")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.nodes.analyze import analyze_matches
from agent.nodes.enrich import enrich_features
from agent.nodes.evaluate import evaluate_predictions
from agent.nodes.fetch import fetch_fixtures
from agent.nodes.insight import generate_insight
from agent.nodes.publish import publish_to_supabase
from agent.nodes.select import select_top


def main() -> dict:
    """Menjalankan pipeline state machine tujuh node secara berurutan."""
    print(f"🚀 Agent mulai: {datetime.now().isoformat()}")

    state = {
        "all_matches": [],
        "selected_matches": [],
        "analyses": [],
        "errors": [],
        "published_count": 0,
        "evaluated_count": 0,
    }

    print("📊 [0/6] Evaluating past predictions...")
    state = evaluate_predictions(state)
    print(f"   → {state['evaluated_count']} predictions evaluated")

    print("📥 [1/6] Fetching fixtures...")
    state = fetch_fixtures(state)
    print(f"   → {len(state['all_matches'])} matches fetched")

    print("🧮 [2/6] Enriching features...")
    state = enrich_features(state)
    print(f"   → {len(state['all_matches'])} matches enriched")

    print("🎯 [3/6] Selecting top matches...")
    state = select_top(state)
    print(f"   → {len(state['selected_matches'])} matches selected")

    print("🧠 [4/6] Analyzing with ML models...")
    state = analyze_matches(state)
    print(f"   → {len(state['analyses'])} analyses generated")

    print("💬 [5/6] Generating insights with LLM...")
    state = generate_insight(state)
    print(f"   → {len(state['analyses'])} insights generated")

    print("💾 [6/6] Publishing to Supabase...")
    state = publish_to_supabase(state)
    print(f"   → {state['published_count']} matches published")

    if state.get("errors"):
        print(f"\n⚠️  {len(state['errors'])} errors:")

        for error in state["errors"]:
            print(f"   - {error}")

    print(f"\n✅ Agent selesai: {datetime.now().isoformat()}")

    return state


if __name__ == "__main__":
    main()

