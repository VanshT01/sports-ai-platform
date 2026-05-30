import type { MatchDetailResponse, MatchesResponse } from "./types";

async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`http://127.0.0.1:8000${path}`);

  if (!response.ok) {
    let message = `Backend error: ${response.status}`;

    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the status-only fallback if the backend did not return JSON.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function fetchMatches(path: string): Promise<MatchesResponse> {
  return fetchApi<MatchesResponse>(path);
}

export function fetchMatchDetail(matchId: string): Promise<MatchDetailResponse> {
  return fetchApi<MatchDetailResponse>(`/matches/${matchId}`);
}
