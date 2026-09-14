<script lang="ts">
  import { onMount } from 'svelte';
  import MatchCard from './lib/MatchCard.svelte';
  import { fetchDaily } from './lib/api';
  import type { Match } from './lib/types';

  let matches = $state<Match[]>([]);
  let loading = $state(true);
  let error = $state('');
  let activeTab = $state<'today' | 'tomorrow'>('today');

  let pageTitle = $derived(activeTab === 'today' ? 'Rekomendasi Hari Ini' : 'Rekomendasi Besok');

  function getDateOffset(offset: number): string | undefined {
    if (offset === 0) return undefined;
    const target = new Date();
    target.setDate(target.getDate() + offset);
    return target.toISOString().slice(0, 10);
  }

  async function loadMatches(offset = 0): Promise<void> {
    loading = true;
    error = '';

    try {
      const response = await fetchDaily(getDateOffset(offset));
      matches = response.matches;
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Terjadi kesalahan saat mengambil data.';
      matches = [];
    } finally {
      loading = false;
    }
  }

  function changeTab(tab: 'today' | 'tomorrow'): void {
    activeTab = tab;
    void loadMatches(tab === 'today' ? 0 : 1);
  }

  onMount(() => {
    void loadMatches();
  });
</script>

<svelte:head>
  <title>Football Analyst PWA</title>
  <meta
    name="description"
    content="Rekomendasi analisis pertandingan sepak bola harian."
  />
</svelte:head>

<div class="app-shell">
  <header class="app-header">
    <div>
      <p class="eyebrow">Analisis pertandingan harian</p>
      <h1>⚽ Football Analyst PWA</h1>
    </div>
    <span class="status-dot" title="Aplikasi aktif"></span>
  </header>

  <nav class="tabs" aria-label="Periode pertandingan">
    <button class:active={activeTab === 'today'} onclick={() => changeTab('today')}>
      Hari Ini
    </button>
    <button class:active={activeTab === 'tomorrow'} onclick={() => changeTab('tomorrow')}>
      Besok
    </button>
  </nav>

  <main>
    <div class="section-heading">
      <div>
        <p class="eyebrow">Peluang terpilih</p>
        <h2>{pageTitle}</h2>
      </div>
      {#if !loading && !error}
        <span class="match-count">{matches.length} match</span>
      {/if}
    </div>

    {#if loading}
      <div class="state-panel" role="status">
        <div class="spinner" aria-hidden="true"></div>
        <p>Memuat rekomendasi...</p>
      </div>
    {:else if error}
      <div class="state-panel error-panel" role="alert">
        <p class="error-title">Data belum dapat dimuat</p>
        <p>{error}</p>
        <button class="retry-button" onclick={() => loadMatches(activeTab === 'today' ? 0 : 1)}>
          Coba lagi
        </button>
      </div>
    {:else if matches.length === 0}
      <div class="state-panel">
        <p class="empty-title">Belum ada rekomendasi</p>
        <p>Belum ada pertandingan yang memenuhi kriteria analisis untuk periode ini.</p>
      </div>
    {:else}
      <section class="match-list" aria-label={pageTitle}>
        {#each matches as match (match.id)}
          <MatchCard {match} />
        {/each}
      </section>
    {/if}
  </main>

  <footer class="app-footer">
    <p>Rekomendasi bersifat analitis, tidak ada jaminan hasil.</p>
  </footer>
</div>

<style>
  .app-shell {
    width: min(100% - 2rem, 960px);
    margin: 0 auto;
    padding: 1.25rem 0 2rem;
  }

  .app-header,
  .section-heading {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .app-header h1,
  .section-heading h2 {
    margin: 0;
    color: #f8fafc;
  }

  .app-header h1 {
    font-size: clamp(1.35rem, 6vw, 2rem);
  }

  .section-heading h2 {
    font-size: clamp(1.25rem, 5vw, 1.65rem);
  }

  .eyebrow {
    margin: 0 0 0.35rem;
    color: #38bdf8;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .status-dot {
    width: 0.65rem;
    height: 0.65rem;
    margin-top: 0.5rem;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 0 0.3rem rgba(34, 197, 94, 0.12);
  }

  .tabs {
    display: flex;
    gap: 0.4rem;
    margin: 1.5rem 0 2rem;
    border-bottom: 1px solid #25253b;
  }

  .tabs button {
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 0.7rem 0.9rem;
    background: transparent;
    color: #64748b;
    cursor: pointer;
    font: inherit;
    font-size: 0.88rem;
    font-weight: 700;
  }

  .tabs button.active {
    border-bottom-color: #38bdf8;
    color: #f8fafc;
  }

  .match-count {
    color: #94a3b8;
    font-size: 0.78rem;
  }

  .match-list {
    display: grid;
    gap: 1rem;
    margin-top: 1rem;
  }

  .state-panel {
    display: grid;
    place-items: center;
    min-height: 12rem;
    margin-top: 1rem;
    border: 1px dashed #2d2d44;
    border-radius: 1rem;
    padding: 1.5rem;
    color: #94a3b8;
    text-align: center;
  }

  .state-panel p {
    margin: 0.35rem 0;
  }

  .error-title,
  .empty-title {
    color: #f8fafc;
    font-weight: 800;
  }

  .error-panel {
    border-color: rgba(251, 191, 36, 0.45);
  }

  .retry-button {
    margin-top: 0.75rem;
    border: 1px solid #38bdf8;
    border-radius: 0.5rem;
    padding: 0.55rem 0.85rem;
    background: rgba(56, 189, 248, 0.1);
    color: #7dd3fc;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
  }

  .spinner {
    width: 1.75rem;
    height: 1.75rem;
    border: 3px solid #2d2d44;
    border-top-color: #38bdf8;
    border-radius: 50%;
    animation: spin 800ms linear infinite;
  }

  .app-footer {
    margin-top: 2rem;
    border-top: 1px solid #25253b;
    padding-top: 1rem;
    color: #64748b;
    font-size: 0.72rem;
    text-align: center;
  }

  .app-footer p {
    margin: 0;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (min-width: 640px) {
    .app-shell {
      padding-top: 2rem;
    }
  }
</style>
