"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  useEffect(() => {
    fetch("/api/settings/status", { cache: "no-store" })
      .then((r) => r.json())
      .then((data) => {
        router.replace(data?.api_key?.ok ? "/chat" : "/welcome");
      })
      .catch(() => router.replace("/chat"));
  }, [router]);
  return null;
}
