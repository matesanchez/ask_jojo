"use client";

import Link from "next/link";

export default function WelcomePage() {
  return (
    <div className="welcome-page">
      <div className="welcome-card">
        <h1 className="welcome-heading">Welcome to JoJo Bot</h1>
        <p className="welcome-description">
          Your department&apos;s AI knowledge assistant. To get started, configure your settings.
        </p>

        <ol className="welcome-steps">
          <li className="welcome-step">
            <span className="welcome-step-num">1</span>
            <span className="welcome-step-text">
              Paste your Anthropic API key in <strong>Settings &rarr; API key</strong>
            </span>
          </li>
          <li className="welcome-step">
            <span className="welcome-step-num">2</span>
            <span className="welcome-step-text">
              Confirm connector paths (OneDrive and public drive) in <strong>Settings &rarr; Connectors</strong>
            </span>
          </li>
          <li className="welcome-step">
            <span className="welcome-step-num">3</span>
            <span className="welcome-step-text">
              Ask JoJo your first question in the <strong>Chat</strong> tab
            </span>
          </li>
        </ol>

        <Link href="/settings" className="welcome-cta">
          Open Settings
        </Link>
      </div>
    </div>
  );
}
