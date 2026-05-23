import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import NavLinks from "./NavLinks";

export const metadata: Metadata = {
  title: "JoJo Bot v2.0",
  description: "Nurix internal knowledge assistant — persistent LLM-compiled wiki.",
};

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
            <Link href="/">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/jojo-avatar.png" alt="" className="jojo-avatar" width={28} height={28} />
              JoJo Bot <span className="jojo-version">v2.0</span>
            </Link>
          </div>
          <nav className="jojo-nav" aria-label="Primary">
            <NavLinks />
          </nav>
        </header>
        <main className="jojo-main">{children}</main>
      </body>
    </html>
  );
}
