import type { DailyResponse, Match } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'https://footballanalystskingzhou30.pythonanywhere.com';

export async function fetchDaily(date?: string): Promise<DailyResponse> {
  const url = new URL(`${API_URL}/api/v1/daily`);
  if (date) url.searchParams.set('date', date);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Gagal fetch rekomendasi: ${response.status}`);
  }

  return response.json() as Promise<DailyResponse>;
}

export async function fetchMatch(id: string): Promise<Match> {
  const response = await fetch(`${API_URL}/api/v1/match/${encodeURIComponent(id)}`);
  if (!response.ok) {
    throw new Error(`Gagal fetch match: ${response.status}`);
  }

  return response.json() as Promise<Match>;
}
