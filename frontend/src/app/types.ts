export type Match = {
  id: number;
  competition: string;
  homeTeam: string;
  awayTeam: string;
  utcDate: string | null;
  status: string;
  matchday: number | null;
  score?: {
    fullTime?: {
      home: number | null;
      away: number | null;
    };
  };
};

export type MatchEvent = {
  elapsed: number | null;
  extra: number | null;
  team: string | null;
  player: string | null;
  assist: string | null;
  type: string | null;
  detail: string | null;
  comments: string | null;
};

export type GroupedMatches = Record<string, Record<string, Match[]>>;

export type MatchesResponse = {
  type: "past";
  count: number;
  groupedMatches?: GroupedMatches;
  matches: Match[];
};

export type MatchDetailResponse = {
  match: Match;
  events: MatchEvent[];
  cachedAt?: string;
};
