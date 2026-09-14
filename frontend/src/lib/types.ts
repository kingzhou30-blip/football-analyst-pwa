export type Category = 'over_under' | 'btts' | 'win' | 'handicap';

export interface MatchAnalysis {
  id: string;
  category: Category;
  pick: string;
  confidence: number;
  odds?: number | null;
  extra?: Record<string, unknown>;
  reason?: string | null;
}

export interface Match {
  id: string;
  match_id: string;
  league: string;
  league_code?: string;
  kickoff: string;
  home_team: string;
  away_team: string;
  match_score: number;
  agent_insight?: string;
  match_analyses: MatchAnalysis[];
}

export interface DailyResponse {
  date: string;
  count: number;
  matches: Match[];
}
