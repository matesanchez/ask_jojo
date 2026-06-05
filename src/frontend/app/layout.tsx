import type { Metadata } from "next";
import Link from "next/link";
// Self-hosted IBM Plex (bundled at build via @fontsource - no network / Google Fonts needed).
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "@fontsource/ibm-plex-sans/600.css";
import "@fontsource/ibm-plex-sans/700.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "@fontsource/ibm-plex-mono/600.css";
import "./globals.css";
import NavLinks from "./NavLinks";
import ThemeToggle from "./ThemeToggle";


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
    <html lang="en">
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
