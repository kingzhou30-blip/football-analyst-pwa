<script lang="ts">
  import type { Category, Match, MatchAnalysis } from './types';
  import PredictionTile from './PredictionTile.svelte';

  interface Props {
    match: Match;
  }

  let { match }: Props = $props();

  const dateFormatter = new Intl.DateTimeFormat('id-ID', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });

  const tileConfig: Array<{ category: Category; icon: string; label: string }> = [
    { category: 'over_under', icon: '⚽', label: 'Over / Under' },
    { category: 'btts', icon: '🎯', label: 'BTTS' },
    { category: 'win', icon: '🏆', label: 'Win' },
    { category: 'handicap', icon: '⚖️', label: 'Handicap' },
  ];

  function getAnalysis(category: Category): MatchAnalysis {
    return (
      match.match_analyses.find((analysis) => analysis.category === category) ?? {
        id: `${match.id}-${category}-empty`,
        category,
        pick: 'Belum tersedia',
        confidence: 0,
      }
    );
  }

  function formatKickoff(value: string): string {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? 'Waktu tidak tersedia' : dateFormatter.format(parsed);
  }
</script>

<article class="match-card">
  <header class="match-header">
    <div class="league-info">
      <span class="league-badge">{match.league_code || match.league}</span>
      <span class="kickoff">{formatKickoff(match.kickoff)}</span>
    </div>
    <span class="match-score">Score {match.match_score.toFixed(1)}</span>
  </header>

  <div class="teams">
    <h2>{match.home_team} <span>vs</span> {match.away_team}</h2>
  </div>

  <div class="prediction-grid">
    {#each tileConfig as tile}
      <PredictionTile
        analysis={getAnalysis(tile.category)}
        icon={tile.icon}
        label={tile.label}
      />
    {/each}
  </div>

  {#if match.agent_insight}
    <footer class="insight">
      <span class="insight-icon" aria-hidden="true">💡</span>
      <p>{match.agent_insight}</p>
    </footer>
  {/if}
</article>

<style>
  .match-card {
    padding: 1rem;
    border: 1px solid #25253b;
    border-radius: 1rem;
    background: #141422;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
  }

  .match-header,
  .league-info {
    display: flex;
    align-items: center;
  }

  .match-header {
    justify-content: space-between;
    gap: 0.75rem;
  }

  .league-info {
    min-width: 0;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .league-badge {
    border-radius: 999px;
    padding: 0.25rem 0.55rem;
    background: rgba(56, 189, 248, 0.12);
    color: #7dd3fc;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .kickoff {
    color: #94a3b8;
    font-size: 0.78rem;
  }

  .match-score {
    flex-shrink: 0;
    color: #fbbf24;
    font-size: 0.78rem;
    font-weight: 800;
  }

  .teams h2 {
    margin: 1rem 0;
    color: #f8fafc;
    font-size: clamp(1rem, 4vw, 1.25rem);
    line-height: 1.3;
  }

  .teams h2 span {
    color: #64748b;
    font-size: 0.8em;
    font-weight: 500;
  }

  .prediction-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem;
  }

  .insight {
    display: flex;
    gap: 0.6rem;
    margin-top: 0.9rem;
    border-top: 1px solid #29293f;
    padding-top: 0.8rem;
    color: #cbd5e1;
    font-size: 0.82rem;
    line-height: 1.5;
  }

  .insight p {
    margin: 0;
  }

  .insight-icon {
    flex-shrink: 0;
  }

  @media (min-width: 640px) {
    .match-card {
      padding: 1.25rem;
    }

    .prediction-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
</style>
