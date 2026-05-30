import type { GroupedMatches, Match } from "../types";
import MatchCard from "./MatchCard";

type GroupedMatchListProps = {
  groupedMatches: GroupedMatches;
  emptyMessage: string;
};

function formatDate(date: string) {
  if (!date) {
    return "Date unavailable";
  }

  return new Date(`${date}T00:00:00Z`).toLocaleDateString(undefined, {
    weekday: "long",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function GroupedMatchList({
  groupedMatches,
  emptyMessage,
}: GroupedMatchListProps) {
  const dates = Object.entries(groupedMatches);

  if (dates.length === 0) {
    return <p className="empty-state">{emptyMessage}</p>;
  }

  return (
    <div className="match-list">
      {dates.map(([date, leagues]) => (
        <section className="date-section" key={date}>
          <h2>{formatDate(date)}</h2>

          {Object.entries(leagues).map(([league, matches]: [string, Match[]]) => (
            <div className="league-block" key={`${date}-${league}`}>
              <div className="league-header">
                <h3>{league}</h3>
                <span>{matches.length} matches</span>
              </div>

              {matches.map((match) => (
                <MatchCard key={match.id} match={match} />
              ))}
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}
