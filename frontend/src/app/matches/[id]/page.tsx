"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { fetchMatchDetail } from "../../api";
import type { MatchDetailResponse, MatchEvent } from "../../types";

function eventMinute(event: MatchEvent) {
  if (event.elapsed === null) {
    return "--";
  }

  return event.extra ? `${event.elapsed}+${event.extra}'` : `${event.elapsed}'`;
}

function eventLabel(event: MatchEvent) {
  return [event.detail, event.comments].filter(Boolean).join(" - ");
}

export default function MatchDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<MatchDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMatchDetail(params.id)
      .then((data) => {
        setDetail(data);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Unable to load match");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [params.id]);

  const groupedEvents = useMemo(() => {
    const groups: Record<string, MatchEvent[]> = {};

    for (const event of detail?.events || []) {
      const key = event.type || "Other";
      groups[key] = [...(groups[key] || []), event];
    }

    return groups;
  }, [detail]);

  if (loading) {
    return <main className="page-shell loading-state">Loading match events...</main>;
  }

  if (error || !detail) {
    return (
      <main className="page-shell">
        <Link className="back-link" href="/past">
          Back to past results
        </Link>
        <p className="error-state">{error || "Match not found"}</p>
      </main>
    );
  }

  const { match } = detail;
  const score = match.score?.fullTime;
  const hasScore = score && score.home !== null && score.away !== null;

  return (
    <main className="page-shell">
      <Link className="back-link" href="/past">
        Back to past results
      </Link>

      <section className="detail-hero">
        <div>
          <span className="eyebrow">{match.competition}</span>
          <h1>
            {match.homeTeam} vs {match.awayTeam}
          </h1>
          <p>{match.utcDate ? new Date(match.utcDate).toLocaleString() : "Date unavailable"}</p>
        </div>

        <div className="detail-score">
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
      </section>

      {detail.cachedAt && (
        <p className="cache-note">
          Showing cached match data from {new Date(detail.cachedAt).toLocaleString()}.
        </p>
      )}

      <section className="events-panel">
        <div className="league-header">
          <h3>Match Events</h3>
          <span>{detail.events.length} events</span>
        </div>

        {detail.events.length === 0 && (
          <p className="empty-state">No event timeline is available for this match yet.</p>
        )}

        {Object.entries(groupedEvents).map(([type, events]) => (
          <div className="event-group" key={type}>
            <h2>{type}</h2>

            <div className="event-list">
              {events.map((event, index) => (
                <article className="event-card" key={`${type}-${index}`}>
                  <span className="event-minute">{eventMinute(event)}</span>
                  <div>
                    <strong>{event.player || event.team || "Match event"}</strong>
                    <p>
                      {event.team}
                      {event.assist ? ` - Assist: ${event.assist}` : ""}
                    </p>
                    {eventLabel(event) && <p>{eventLabel(event)}</p>}
                  </div>
                </article>
              ))}
            </div>
          </div>
        ))}
      </section>
    </main>
  );
}
