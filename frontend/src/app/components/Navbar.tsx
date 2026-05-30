import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link className="brand" href="/">
        <span className="brand-mark">FA</span>
        <span>Football AI</span>
      </Link>

      <div className="nav-links">
        <Link href="/">Home</Link>
        <Link href="/past">Past</Link>
      </div>
    </nav>
  );
}
