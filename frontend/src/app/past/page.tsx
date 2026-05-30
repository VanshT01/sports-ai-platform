"use client";

import { useEffect, useState } from "react";
import { fetchMatches } from "../api";
import GroupedMatchList from "../components/GroupedMatchList";
import type { GroupedMatches } from "../types";

export default function PastPage() {
  const [groupedMatches, setGroupedMatches] = useState<GroupedMatches>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMatches("/matches/past")
      .then((data) => {
        setGroupedMatches(data.groupedMatches || {});
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Unable to load matches");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <main className="page-shell loading-state">Loading results...</main>;
  }

  return (
    <main className="page-shell">
      <header className="page-header">
        <span className="eyebrow">Result archive</span>
        <h1>Past Matches</h1>
      </header>

      {error && <p className="error-state">{error}</p>}
      {!error && (
        <GroupedMatchList
          groupedMatches={groupedMatches}
          emptyMessage="No past matches found."
        />
      )}
    </main>
  );
}
