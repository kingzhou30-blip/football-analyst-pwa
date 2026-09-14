<script lang="ts">
  import type { MatchAnalysis } from './types';

  interface Props {
    analysis: MatchAnalysis;
    icon: string;
    label: string;
  }

  let { analysis, icon, label }: Props = $props();
  let isHighConfidence = $derived(analysis.confidence >= 70);
</script>

<article class:high-confidence={isHighConfidence} class="prediction-tile">
  <div class="tile-heading">
    <span class="tile-icon" aria-hidden="true">{icon}</span>
    <span class="tile-label">{label}</span>
  </div>

  <p class="tile-pick">{analysis.pick}</p>

  <div class="tile-meta">
    <span class="confidence">{analysis.confidence.toFixed(1)}%</span>
    {#if analysis.odds !== null && analysis.odds !== undefined}
      <span class="odds">@ {analysis.odds.toFixed(2)}</span>
    {/if}
  </div>
</article>

<style>
  .prediction-tile {
    min-width: 0;
    padding: 0.75rem;
    border: 1px solid #2d2d44;
    border-radius: 0.75rem;
    background: #0f0f1a;
    transition: border-color 160ms ease, transform 160ms ease;
  }

  .prediction-tile:hover {
    transform: translateY(-1px);
    border-color: #4b4b70;
  }

  .prediction-tile.high-confidence {
    border-color: #22c55e;
    box-shadow: inset 0 0 0 1px rgba(34, 197, 94, 0.18);
  }

  .tile-heading {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    color: #94a3b8;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .tile-icon {
    font-size: 1rem;
  }

  .tile-pick {
    overflow: hidden;
    margin: 0.65rem 0 0.5rem;
    color: #f8fafc;
    font-size: 0.9rem;
    font-weight: 800;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .tile-meta {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.4rem;
    font-size: 0.72rem;
  }

  .confidence {
    color: #38bdf8;
    font-weight: 800;
  }

  .high-confidence .confidence {
    color: #4ade80;
  }

  .odds {
    color: #94a3b8;
  }
</style>
