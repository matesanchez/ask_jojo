export default function HomePage() {
  return (
    <section className="jojo-placeholder">
      <span className="phase-tag">Phase 0 skeleton</span>
      <h1>JoJo Bot v2.0</h1>
      <p>
        Nurix internal knowledge assistant. Phase 0 scaffold is live — the
        navigation header is pinned so later phases fill in tabs without
        touching it.
      </p>
      <p>
        Start with the <a href="/wiki">Wiki</a> tab to see the navigation anchor
        in place. Real content lands phase by phase; see{" "}
        <code>ask_jojo/PLAN.md</code> and <code>ask_jojo/docs/v2_status.md</code>.
      </p>
    </section>
  );
}
