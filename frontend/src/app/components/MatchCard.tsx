import Link from "next/link";
import type { Match } from "../types";

export default function MatchCard({ match }: { match: Match }) {
  const score = match.score?.fullTime;
  const hasScore = score && score.home !== null && score.away !== null;

  return (
    <Link className="match-card match-card-link" href={`/matches/${match.id}`}>
      <div className="match-meta">
        <span className="status-pill">{match.status}</span>
        <time>
          {match.utcDate ? new Date(match.utcDate).toLocaleString() : "TBD"}
        </time>
      </div>

      <div className="match-row">
        <div className="team team-home">
          <span>{match.homeTeam}</span>
        </div>

        <div className="scoreboard">
          {hasScore ? (
            <>
              <strong>{score.home}</strong>
              <span>-</span>
              <strong>{score.away}</strong>
            </>
          ) : (
            <span>vs</span>
          )}
        </div>

        <div className="team team-away">
          <span>{match.awayTeam}</span>
        </div>
      </div>

      <div className="match-footer">
        <span>{match.competition}</span>
        <span>View match events</span>
      </div>
    </Link>
  );
}
