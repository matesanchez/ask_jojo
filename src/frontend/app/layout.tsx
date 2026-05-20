import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "JoJo Bot v2.0",
  description: "Nurix internal knowledge assistant — persistent LLM-compiled wiki.",
};

const TABS: { href: string; label: string }[] = [
  { href: "/chat",     label: "Chat" },
  { href: "/wiki",     label: "Wiki" },
  { href: "/raw",      label: "Raw" },
  { href: "/graph",    label: "Graph" },
  { href: "/ops",      label: "Ops" },
  { href: "/settings", label: "Settings" },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="jojo-header">
          <div className="jojo-brand">
            <Link href="/">JoJo Bot <span className="jojo-version">v2.0</span></Link>
          </div>
          <nav className="jojo-nav" aria-label="Primary">
            {TABS.map((t) => (
              <Link key={t.href} href={t.href} className="jojo-nav-link">
                {t.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="jojo-main">{children}</main>
      </body>
    </html>
  );
}
