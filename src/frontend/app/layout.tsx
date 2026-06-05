import type { Metadata } from "next";
import Link from "next/link";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import NavLinks from "./NavLinks";
import ThemeToggle from "./ThemeToggle";

const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-plex-sans",
  display: "swap",
});
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "JoJo Bot v2.0",
  description: "Nurix internal knowledge assistant — persistent LLM-compiled wiki.",
};

// Set the theme before first paint to avoid a flash of the wrong theme.
const themeInit = `(function(){try{var t=localStorage.getItem('jojo-theme');if(t!=='light'&&t!=='dark'){t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${plexSans.variable} ${plexMono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
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
          <ThemeToggle />
        </header>
        <main className="jojo-main">{children}</main>
      </body>
    </html>
  );
}
