export default function WikiPage() {
  return (
    <section className="jojo-placeholder">
      <span className="phase-tag">Phase 1 coming soon</span>
      <h1>Wiki</h1>
      <p>
        The Wiki tab will show the compiled <code>ask_jojo_wiki/</code> tree,
        markdown previews, frontmatter panels, and wikilink auto-complete. It
        lands in Phase 3 after the ingest pipeline (Phase 1) and the absorb
        loop (Phase 2) produce real content.
      </p>
      <p>
        For now this placeholder exists only to create the navigation anchor so
        the header is stable across phases. See{" "}
        <code>ask_jojo/PLAN.md</code> §6 Phase 3.
      </p>
    </section>
  );
}
