"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS: { href: string; label: string }[] = [
  { href: "/chat",     label: "Chat" },
  { href: "/wiki",     label: "Wiki" },
  { href: "/raw",      label: "Raw" },
  { href: "/graph",    label: "Graph" },
  { href: "/ops",      label: "Ops" },
  { href: "/settings", label: "Settings" },
];

export default function NavLinks() {
  const pathname = usePathname();
  return (
    <>
      {TABS.map((t) => (
        <Link
          key={t.href}
          href={t.href}
          className={"jojo-nav-link" + (pathname?.startsWith(t.href) ? " active" : "")}
        >
          {t.label}
        </Link>
      ))}
    </>
  );
}
