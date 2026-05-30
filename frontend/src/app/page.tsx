import Link from "next/link";

export default function Home() {
  return (
    <main className="page-shell home-shell">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Match intelligence</span>
          <h1>Football AI Dashboard</h1>
          <p>
            Past results across elite competitions with match timelines for
            goals, cards, substitutions, penalties, and other key events.
          </p>
        </div>

        <div className="hero-actions">
          <Link className="action-link action-primary" href="/past">
            Past Results
          </Link>
        </div>
      </section>

      <section className="overview-grid" aria-label="Dashboard sections">
        <Link className="overview-panel" href="/past">
          <span>Past</span>
          <strong>Recent results and events</strong>
        </Link>
      </section>
    </main>
  );
}
